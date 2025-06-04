#!/bin/bash

# Treat unset variables as an error when substituting.
set -u

# --- Configuration ---
PROJECT_ROOT_DIR=$(pwd)
SRC_MODULE_BASE="building_intelligent_agents"
SRC_CODE_DIR="${PROJECT_ROOT_DIR}/src/${SRC_MODULE_BASE}"
SCRIPT_TIMEOUT="30s" # Increased timeout significantly
INTER_TEST_DELAY="5s"  # Delay between tests

: "${TIMEOUT_COMMAND_OVERRIDE:=}"

# --- Helper Functions ---
log_info() { echo "[INFO] $1"; }
log_success() { echo "[PASS] $1"; }
log_error() { echo "[FAIL] $1"; }
log_skip() { echo "[SKIP] $1"; }

# --- Pre-run Checks ---
log_info "Starting CLI Example Test Runner..."
TIMEOUT_CMD=""
log_info "Verifying timeout command..."
if [ -n "$TIMEOUT_COMMAND_OVERRIDE" ]; then
    if command -v "$TIMEOUT_COMMAND_OVERRIDE" >/dev/null 2>&1; then
        TIMEOUT_CMD=$(command -v "$TIMEOUT_COMMAND_OVERRIDE")
        log_info "Using overridden timeout command: ${TIMEOUT_CMD}"
    else
        log_error "Overridden timeout command '$TIMEOUT_COMMAND_OVERRIDE' not found."
        exit 1
    fi
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD=$(command -v gtimeout)
    log_info "'gtimeout' (macOS) command is available at: ${TIMEOUT_CMD}"
elif command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD=$(command -v timeout)
    log_info "'timeout' command is available at: ${TIMEOUT_CMD}"
else
    log_error "'timeout' or 'gtimeout' command not found. Install coreutils or gnu-coreutils."
    exit 1
fi

PYTHON_EXE=""
if [ -z "${VIRTUAL_ENV:-}" ]; then
    log_error "VIRTUAL_ENV not set. Activate your virtual environment."
    exit 1
fi
log_info "VIRTUAL_ENV is set to: '${VIRTUAL_ENV}'"
potential_python_exe_unix="${VIRTUAL_ENV}/bin/python"
potential_python_exe_windows="${VIRTUAL_ENV}/Scripts/python.exe"
if [ -f "${potential_python_exe_unix}" ]; then PYTHON_EXE="${potential_python_exe_unix}"; 
elif [ -f "${potential_python_exe_windows}" ]; then PYTHON_EXE="${potential_python_exe_windows}"; 
else
    log_error "Python executable not found in VIRTUAL_ENV paths."
    exit 1
fi
log_info "Determined PYTHON_EXE to be: '${PYTHON_EXE}'"
if ! "${PYTHON_EXE}" --version >/dev/null 2>&1; then
    log_error "PYTHON_EXE ('${PYTHON_EXE}') is not a valid Python interpreter."
    exit 1
fi
log_info "PYTHON_EXE version: $(${PYTHON_EXE} --version)"

if [ ! -f "${PROJECT_ROOT_DIR}/.env" ]; then
    log_info "Warning: '.env' file not found in project root. API-dependent examples may fail."
fi

log_info "Project Root: ${PROJECT_ROOT_DIR}"
log_info "Source Directory: ${SRC_CODE_DIR}"
log_info "Timeout per script: ${SCRIPT_TIMEOUT} using command ${TIMEOUT_CMD}"
log_info "Delay between tests: ${INTER_TEST_DELAY}"
echo "----------------------------------------------------------------------"


RESULTS_FILE="/tmp/adk_test_results.txt"
> "${RESULTS_FILE}"

declare -a files_to_process=()
TOTAL_FILES_WITH_MAIN_BLOCK=0
TEMP_FIND_OUTPUT=$(mktemp)
find "${SRC_CODE_DIR}" -type f -name "*.py" ! -name "__init__.py" ! -name "utils.py" -print0 > "${TEMP_FIND_OUTPUT}"
while IFS= read -r -d $'\0' py_file_path; do
    if [ -z "$py_file_path" ]; then continue; fi
    if grep -q 'if __name__ == "__main__":' "$py_file_path"; then
        files_to_process+=("$py_file_path")
        TOTAL_FILES_WITH_MAIN_BLOCK=$((TOTAL_FILES_WITH_MAIN_BLOCK + 1))
    else
        log_info "Skipping (no __main__ block): ${py_file_path#${PROJECT_ROOT_DIR}/}"
    fi
done < "${TEMP_FIND_OUTPUT}"
rm "${TEMP_FIND_OUTPUT}"

log_info "Found ${TOTAL_FILES_WITH_MAIN_BLOCK} Python files with a '__main__' block to process."
echo "----------------------------------------------------------------------"

for py_file_path in "${files_to_process[@]}"; do
    if [ -z "$py_file_path" ]; then
        log_error "Encountered empty py_file_path in loop. Skipping."
        continue
    fi
    (
        set +e # Ensure this iteration's logging completes

        relative_path_from_src_dir="${py_file_path#${PROJECT_ROOT_DIR}/src/}"
        module_path_slashes="${relative_path_from_src_dir%.py}"
        module_path_dots="${module_path_slashes//\//.}"

        if [[ "${module_path_dots}" == *".chapter20.my_simple_echo_agent.test_agent"* ]]; then
            log_skip "Module ${module_path_dots} (Requires deployed Reasoning Engine)"
            echo "${module_path_dots} SKIPPED_EXPLICITLY" >> "${RESULTS_FILE}"
            exit 0 # Exit this subshell cleanly if skipped
        fi

        log_info "--- Preparing to run module: ${module_path_dots} ---"
        
        execution_output_line=""
        timeout_exit_code=0
        script_output_capture_file="/tmp/adk_script_stdout_${module_path_dots//./_}.log"
        script_error_capture_file="/tmp/adk_script_stderr_${module_path_dots//./_}.log"
        # Clear previous logs for this script
        > "${script_output_capture_file}" 
        > "${script_error_capture_file}"

        unset PYTHONPATH
        # Capture stdout to one file, stderr to another
        "${TIMEOUT_CMD}" "${SCRIPT_TIMEOUT}" "${PYTHON_EXE}" -m "${module_path_dots}" >"${script_output_capture_file}" 2>"${script_error_capture_file}"
        timeout_exit_code=$?

        if [ ${timeout_exit_code} -eq 0 ]; then
            log_success "Module ${module_path_dots}"
            execution_output_line="${module_path_dots} PASSED"
            rm -f "${script_output_capture_file}" "${script_error_capture_file}" # Clean up logs on success
        else
            # Preserve logs on failure for inspection
            log_error "Module ${module_path_dots} FAILED. Stdout: ${script_output_capture_file}, Stderr: ${script_error_capture_file}"
            if [ ${timeout_exit_code} -eq 124 ]; then
                log_error "    Reason: TIMED OUT after ${SCRIPT_TIMEOUT}"
                execution_output_line="${module_path_dots} FAILED_TIMEOUT_${timeout_exit_code}"
            elif [ ${timeout_exit_code} -eq 127 ]; then
                 log_error "    Reason: Command not found by ${TIMEOUT_CMD} for '${PYTHON_EXE}' (Exit code: ${timeout_exit_code})"
                 execution_output_line="${module_path_dots} FAILED_CMDNOTFOUND_${timeout_exit_code}"
            else
                log_error "    Reason: Python script exited with code ${timeout_exit_code}"
                execution_output_line="${module_path_dots} FAILED_PYTHON_${timeout_exit_code}"
            fi
        fi
        
        echo "${execution_output_line}" >> "${RESULTS_FILE}"
        
    ) # End of subshell for this iteration's logic
    
    log_info "Waiting ${INTER_TEST_DELAY} before next test..."
    sleep "${INTER_TEST_DELAY}"
    echo "----------------------------------------------------------------------"
done


PROCESSED_IN_LOOP_COUNT=0
if [ -f "${RESULTS_FILE}" ]; then
    PROCESSED_IN_LOOP_COUNT=$(wc -l < "${RESULTS_FILE}" | awk '{print $1}')
fi

PASSED_COUNT=0
FAILED_COUNT=0
SKIPPED_EXPLICITLY_COUNT=0
FAILED_TESTS=()
SKIPPED_TESTS=()

if [ -f "${RESULTS_FILE}" ]; then
    while IFS= read -r line; do
        module_name=$(echo "$line" | awk '{print $1}')
        status_field=$(echo "$line" | awk '{print $2}')
        if [ -z "$module_name" ] || [ -z "$status_field" ]; then continue; fi
        case "$status_field" in
            PASSED) PASSED_COUNT=$((PASSED_COUNT + 1));;
            SKIPPED_EXPLICITLY)
                SKIPPED_EXPLICITLY_COUNT=$((SKIPPED_EXPLICITLY_COUNT + 1))
                SKIPPED_TESTS+=("${module_name}")
                ;;
            FAILED_TIMEOUT_*|FAILED_CMDNOTFOUND_*|FAILED_PYTHON_*)
                FAILED_COUNT=$((FAILED_COUNT + 1))
                error_reason_type=$(echo "$status_field" | awk -F_ '{print $2}')
                exit_code_val=$(echo "$status_field" | awk -F_ '{print $NF}')
                FAILED_TESTS+=("${module_name} (Reason: ${error_reason_type} Code: ${exit_code_val})")
                ;;
            *)
                log_error "Unknown status: ${module_name} ${status_field}"; FAILED_COUNT=$((FAILED_COUNT + 1))
                FAILED_TESTS+=("${module_name} (Reason: Unknown '${status_field}')");;
        esac
    done < "${RESULTS_FILE}"
    log_info "Results file '${RESULTS_FILE}' processed."
fi

echo ""
echo "==================== TEST SUMMARY ===================="
TOTAL_PY_FILES_CHECKED=$( (find "${SRC_CODE_DIR}" -type f -name "*.py" ! -name "__init__.py" ! -name "utils.py" -print0 | tr -dc '\0' | wc -c) || echo "0" )
log_info  "Total Python scripts found (excluding __init__, utils): ${TOTAL_PY_FILES_CHECKED}"
log_info  "Python scripts identified with a '__main__' block: ${TOTAL_FILES_WITH_MAIN_BLOCK}"
log_info  "Scripts processed by the test loop (entries in results file): ${PROCESSED_IN_LOOP_COUNT}"
echo "----------------------------------------------------"
log_success "Passed: ${PASSED_COUNT}"
log_error   "Failed: ${FAILED_COUNT}"
log_skip    "Skipped (explicitly by script logic): ${SKIPPED_EXPLICITLY_COUNT}"
echo "===================================================="

if [ ${FAILED_COUNT} -gt 0 ]; then
    log_error "Details of failed tests:"
    for test_name in "${FAILED_TESTS[@]}"; do
        echo "  - ${test_name}"
    done
    log_info "NOTE: For failed Python scripts, their stdout and stderr have been captured to files in /tmp/ like adk_script_stdout_module_name.log and adk_script_stderr_module_name.log"
fi
if [ ${SKIPPED_EXPLICITLY_COUNT} -gt 0 ]; then
    log_skip "Details of explicitly skipped tests:"
    for test_name in "${SKIPPED_TESTS[@]}"; do
        echo "  - ${test_name}"
    done
fi
echo "======================================================"

if [ "${PROCESSED_IN_LOOP_COUNT}" -ne "${TOTAL_FILES_WITH_MAIN_BLOCK}" ]; then
    UNPROCESSED_COUNT=$((TOTAL_FILES_WITH_MAIN_BLOCK - PROCESSED_IN_LOOP_COUNT))
    if [ ${UNPROCESSED_COUNT} -gt 0 ]; then
        log_error "WARNING: ${UNPROCESSED_COUNT} script(s) with a '__main__' block appear to have been MISSED by the processing loop."
    fi
fi

if [ ${FAILED_COUNT} -eq 0 ]; then
    if [ "${PROCESSED_IN_LOOP_COUNT}" -eq "${TOTAL_FILES_WITH_MAIN_BLOCK}" ]; then
        log_success "All runnable CLI tests passed or were explicitly skipped, and all expected scripts were processed!"
        exit 0
    else
        log_error "No tests failed, but not all expected scripts were processed. Please review warnings."
        exit 1
    fi
else
    log_error "Some CLI tests failed."
    exit 1
fi