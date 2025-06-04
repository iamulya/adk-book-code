#!/bin/bash

set -u

PROJECT_ROOT_DIR=$(pwd)
SRC_MODULE_BASE="building_intelligent_agents"
SRC_CODE_DIR="${PROJECT_ROOT_DIR}/src/${SRC_MODULE_BASE}"
SCRIPT_TIMEOUT="30s"
INTER_TEST_DELAY="3s" # Reduced slightly from 5s, adjust as needed

: "${TIMEOUT_COMMAND_OVERRIDE:=}"

# --- List of module paths known to be interactive and should be skipped ---
# (Use the dot-separated module path as it would be used with `python -m`)
declare -a KNOWN_INTERACTIVE_SCRIPTS_TO_SKIP=(
    "building_intelligent_agents.chapter1.simple_assistant"       # Example, as it has input() in its __main__
    "building_intelligent_agents.chapter5.user_profile_tool"    # Has input() in its __main__
    "building_intelligent_agents.chapter6.choice_agent"         # Complex input loop in __main__
    # Add other known interactive scripts here if you find them
)

# --- Helper Functions ---
log_info() { echo "[INFO] $1"; }
log_success() { echo "[PASS] $1"; }
log_error() { echo "[FAIL] $1"; }
log_skip() { echo "[SKIP] $1"; }

is_in_array() {
    local needle="$1"
    shift
    local hay; for hay; do [[ "$hay" == "$needle" ]] && return 0; done
    return 1
}

# --- Pre-run Checks ---
# ... (Keep the pre-run checks for TIMEOUT_CMD, PYTHON_EXE, .env as they were)
# (Condensed for brevity, assume they are correctly copied from previous version)
log_info "Starting CLI Example Test Runner..."
TIMEOUT_CMD=""
log_info "Verifying timeout command..."
if [ -n "$TIMEOUT_COMMAND_OVERRIDE" ]; then
    if command -v "$TIMEOUT_COMMAND_OVERRIDE" >/dev/null 2>&1; then TIMEOUT_CMD=$(command -v "$TIMEOUT_COMMAND_OVERRIDE"); log_info "Using overridden: ${TIMEOUT_CMD}"; else log_error "Override '$TIMEOUT_COMMAND_OVERRIDE' not found."; exit 1; fi
elif command -v gtimeout >/dev/null 2>&1; then TIMEOUT_CMD=$(command -v gtimeout); log_info "'gtimeout' found: ${TIMEOUT_CMD}";
elif command -v timeout >/dev/null 2>&1; then TIMEOUT_CMD=$(command -v timeout); log_info "'timeout' found: ${TIMEOUT_CMD}";
else log_error "timeout/gtimeout not found."; exit 1; fi

PYTHON_EXE=""
if [ -z "${VIRTUAL_ENV:-}" ]; then log_error "VIRTUAL_ENV not set."; exit 1; fi
log_info "VIRTUAL_ENV: '${VIRTUAL_ENV}'"
potential_python_exe_unix="${VIRTUAL_ENV}/bin/python"; potential_python_exe_windows="${VIRTUAL_ENV}/Scripts/python.exe"
if [ -f "${potential_python_exe_unix}" ]; then PYTHON_EXE="${potential_python_exe_unix}"; 
elif [ -f "${potential_python_exe_windows}" ]; then PYTHON_EXE="${potential_python_exe_windows}"; 
else log_error "Python exe not found in VIRTUAL_ENV paths."; exit 1; fi
log_info "PYTHON_EXE: '${PYTHON_EXE}'"
if ! "${PYTHON_EXE}" --version >/dev/null 2>&1; then log_error "PYTHON_EXE not valid."; exit 1; fi
log_info "$(${PYTHON_EXE} --version)"
if [ ! -f "${PROJECT_ROOT_DIR}/.env" ]; then log_info "Warning: .env not found."; fi
log_info "Timeout: ${SCRIPT_TIMEOUT}, Delay: ${INTER_TEST_DELAY}"
echo "----------------------------------------------------------------------"


RESULTS_FILE="/tmp/adk_test_results.txt"; > "${RESULTS_FILE}"
declare -a files_to_process=(); TOTAL_FILES_WITH_MAIN_BLOCK=0
TEMP_FIND_OUTPUT=$(mktemp)
find "${SRC_CODE_DIR}" -type f -name "*.py" ! -name "__init__.py" ! -name "utils.py" -print0 > "${TEMP_FIND_OUTPUT}"
while IFS= read -r -d $'\0' py_file_path; do
    if [ -z "$py_file_path" ]; then continue; fi
    if grep -q 'if __name__ == "__main__":' "$py_file_path"; then
        files_to_process+=("$py_file_path")
        TOTAL_FILES_WITH_MAIN_BLOCK=$((TOTAL_FILES_WITH_MAIN_BLOCK + 1))
    else
        # log_info "Skipping (no __main__ block): ${py_file_path#${PROJECT_ROOT_DIR}/}" # Can be verbose
        :
    fi
done < "${TEMP_FIND_OUTPUT}"; rm "${TEMP_FIND_OUTPUT}"
log_info "Found ${TOTAL_FILES_WITH_MAIN_BLOCK} Python files with a '__main__' block to process."
echo "----------------------------------------------------------------------"

SKIPPED_INTERACTIVE_COUNT=0
SKIPPED_INTERACTIVE_LIST=()

for py_file_path in "${files_to_process[@]}"; do
    if [ -z "$py_file_path" ]; then log_error "Empty py_file_path in loop."; continue; fi
    
    relative_path_from_src_dir="${py_file_path#${PROJECT_ROOT_DIR}/src/}"
    module_path_slashes="${relative_path_from_src_dir%.py}"
    module_path_dots="${module_path_slashes//\//.}"

    # --- Begin Skip Logic ---
    # Reason 1: Explicitly configured for manual skip (e.g., requires external setup)
    if [[ "${module_path_dots}" == *".chapter20.my_simple_echo_agent.test_agent"* ]]; then
        log_skip "Module ${module_path_dots} (Reason: Requires deployed Reasoning Engine)"
        echo "${module_path_dots} SKIPPED_MANUAL_CONFIG" >> "${RESULTS_FILE}"
        echo "----------------------------------------------------------------------"
        sleep 0.1 # Small delay to ensure log order
        continue
    fi

    # Reason 2: Known interactive script from the list
    if is_in_array "${module_path_dots}" "${KNOWN_INTERACTIVE_SCRIPTS_TO_SKIP[@]}"; then
        log_skip "Module ${module_path_dots} (Reason: Known interactive script)"
        echo "${module_path_dots} SKIPPED_INTERACTIVE_LIST" >> "${RESULTS_FILE}"
        SKIPPED_INTERACTIVE_COUNT=$((SKIPPED_INTERACTIVE_COUNT + 1)) # Count separately for summary
        SKIPPED_INTERACTIVE_LIST+=("${module_path_dots} (known interactive)")
        echo "----------------------------------------------------------------------"
        sleep 0.1
        continue
    fi

    # Reason 3: Heuristic check for 'input(' within the __main__ block
    # This is more complex with grep as __main__ can span multiple lines
    # A simpler, though less precise, check is for 'input(' anywhere in the file.
    # Or, more targeted: check if 'if __name__ == "__main__":' block contains 'input('.
    # For simplicity now, let's check the whole file for 'input('.
    # This might have false positives if 'input(' is in comments/strings outside of execution path.
    if grep -E 'input\s*\(' "$py_file_path" &>/dev/null; then
        # Further check if it's likely in the __main__ execution path. This is hard.
        # Let's assume for now if 'input(' is present, it's a candidate for skipping.
        # You might need to refine this or rely more on the KNOWN_INTERACTIVE_SCRIPTS_TO_SKIP list.
        log_skip "Module ${module_path_dots} (Reason: Heuristic found 'input(' - potential user input)"
        echo "${module_path_dots} SKIPPED_INTERACTIVE_HEURISTIC" >> "${RESULTS_FILE}"
        SKIPPED_INTERACTIVE_COUNT=$((SKIPPED_INTERACTIVE_COUNT + 1))
        SKIPPED_INTERACTIVE_LIST+=("${module_path_dots} (heuristic 'input()')")
        echo "----------------------------------------------------------------------"
        sleep 0.1
        continue
    fi
    # --- End Skip Logic ---

    # If not skipped, proceed to run the test
    (
        set +e # Ensure this iteration's logging completes

        log_info "--- Preparing to run module: ${module_path_dots} ---"
        
        execution_output_line=""
        timeout_exit_code=0
        # Using mktemp for unique log file names
        script_output_capture_file=$(mktemp "/tmp/adk_stdout_${module_path_dots//./_}_XXXXXX.log")
        script_error_capture_file=$(mktemp "/tmp/adk_stderr_${module_path_dots//./_}_XXXXXX.log")

        unset PYTHONPATH
        "${TIMEOUT_CMD}" "${SCRIPT_TIMEOUT}" "${PYTHON_EXE}" -m "${module_path_dots}" >"${script_output_capture_file}" 2>"${script_error_capture_file}"
        timeout_exit_code=$?

        if [ ${timeout_exit_code} -eq 0 ]; then
            log_success "Module ${module_path_dots}"
            execution_output_line="${module_path_dots} PASSED"
            rm -f "${script_output_capture_file}" "${script_error_capture_file}"
        else
            log_error "Module ${module_path_dots} FAILED. Stdout: ${script_output_capture_file}, Stderr: ${script_error_capture_file}"
            if [ ${timeout_exit_code} -eq 124 ]; then
                log_error "    Reason: TIMED OUT after ${SCRIPT_TIMEOUT}"
                execution_output_line="${module_path_dots} FAILED_TIMEOUT_${timeout_exit_code}"
            elif [ ${timeout_exit_code} -eq 127 ]; then
                 log_error "    Reason: CMDNOTFOUND by ${TIMEOUT_CMD} for '${PYTHON_EXE}' (Code: ${timeout_exit_code})"
                 execution_output_line="${module_path_dots} FAILED_CMDNOTFOUND_${timeout_exit_code}"
            else
                log_error "    Reason: Python script exited with code ${timeout_exit_code}"
                execution_output_line="${module_path_dots} FAILED_PYTHON_${timeout_exit_code}"
            fi
        fi
        echo "${execution_output_line}" >> "${RESULTS_FILE}"
        
    ) 
    
    log_info "Waiting ${INTER_TEST_DELAY} before next test..."
    sleep "${INTER_TEST_DELAY}"
    echo "----------------------------------------------------------------------"
done


PROCESSED_IN_LOOP_COUNT=0; if [ -f "${RESULTS_FILE}" ]; then PROCESSED_IN_LOOP_COUNT=$(wc -l < "${RESULTS_FILE}" | awk '{print $1}'); fi
PASSED_COUNT=0; FAILED_COUNT=0; SKIPPED_MANUAL_CONFIG_COUNT=0; SKIPPED_INTERACTIVE_LIST_COUNT=0; SKIPPED_INTERACTIVE_HEURISTIC_COUNT=0
FAILED_TESTS=(); SKIPPED_MANUAL_CONFIG_LIST=(); SKIPPED_INTERACTIVE_FINAL_LIST=()

if [ -f "${RESULTS_FILE}" ]; then
    while IFS= read -r line; do
        module_name=$(echo "$line" | awk '{print $1}')
        status_field=$(echo "$line" | awk '{print $2}')
        if [ -z "$module_name" ] || [ -z "$status_field" ]; then continue; fi
        case "$status_field" in
            PASSED) PASSED_COUNT=$((PASSED_COUNT + 1));;
            SKIPPED_MANUAL_CONFIG) SKIPPED_MANUAL_CONFIG_COUNT=$((SKIPPED_MANUAL_CONFIG_COUNT + 1)); SKIPPED_MANUAL_CONFIG_LIST+=("${module_name} (manual config)");;
            SKIPPED_INTERACTIVE_LIST) SKIPPED_INTERACTIVE_LIST_COUNT=$((SKIPPED_INTERACTIVE_LIST_COUNT + 1)); SKIPPED_INTERACTIVE_FINAL_LIST+=("${module_name} (known interactive)");;
            SKIPPED_INTERACTIVE_HEURISTIC) SKIPPED_INTERACTIVE_LIST_COUNT=$((SKIPPED_INTERACTIVE_LIST_COUNT + 1)); SKIPPED_INTERACTIVE_FINAL_LIST+=("${module_name} (heuristic 'input()')");;
            FAILED_TIMEOUT_*|FAILED_CMDNOTFOUND_*|FAILED_PYTHON_*)
                FAILED_COUNT=$((FAILED_COUNT + 1))
                error_reason_type=$(echo "$status_field" | awk -F_ '{print $2}')
                exit_code_val=$(echo "$status_field" | awk -F_ '{print $NF}')
                FAILED_TESTS+=("${module_name} (Reason: ${error_reason_type} Code: ${exit_code_val})")
                ;;
            *) log_error "Unknown status: ${module_name} ${status_field}"; FAILED_COUNT=$((FAILED_COUNT + 1)); FAILED_TESTS+=("${module_name} (Unknown '${status_field}')");;
        esac
    done < "${RESULTS_FILE}"
    log_info "Results file '${RESULTS_FILE}' processed."
fi

TOTAL_SKIPPED_COUNT=$((SKIPPED_MANUAL_CONFIG_COUNT + SKIPPED_INTERACTIVE_LIST_COUNT))


echo ""
echo "==================== TEST SUMMARY ===================="
TOTAL_PY_FILES_CHECKED=$( (find "${SRC_CODE_DIR}" -type f -name "*.py" ! -name "__init__.py" ! -name "utils.py" -print0 | tr -dc '\0' | wc -c) || echo "0" )
log_info  "Total Python scripts found (excluding __init__, utils): ${TOTAL_PY_FILES_CHECKED}"
log_info  "Python scripts identified with a '__main__' block: ${TOTAL_FILES_WITH_MAIN_BLOCK}"
log_info  "Scripts processed by the test loop (entries in results file): ${PROCESSED_IN_LOOP_COUNT}"
echo "----------------------------------------------------"
log_success "Passed: ${PASSED_COUNT}"
log_error   "Failed: ${FAILED_COUNT}"
log_skip    "Skipped (Total): ${TOTAL_SKIPPED_COUNT}"
log_skip    "  - Skipped (Manual Config / External Setup): ${SKIPPED_MANUAL_CONFIG_COUNT}"
log_skip    "  - Skipped (Interactive - Known or Heuristic): ${SKIPPED_INTERACTIVE_LIST_COUNT}" # Combined count
echo "===================================================="

if [ ${FAILED_COUNT} -gt 0 ]; then
    log_error "Details of failed tests:"
    for test_name in "${FAILED_TESTS[@]}"; do echo "  - ${test_name}"; done
    log_info "NOTE: For failed Python scripts, their stdout/stderr logs are in /tmp/"
fi
if [ ${SKIPPED_MANUAL_CONFIG_COUNT} -gt 0 ]; then
    log_skip "Details of tests skipped due to requiring manual configuration:"
    for test_name in "${SKIPPED_MANUAL_CONFIG_LIST[@]}"; do echo "  - ${test_name}"; done
fi
if [ ${SKIPPED_INTERACTIVE_LIST_COUNT} -gt 0 ]; then # Combined list from known + heuristic
    log_skip "Details of tests skipped because they are (likely) interactive:"
    # Sort and unique the list for cleaner output
    printf '%s\n' "${SKIPPED_INTERACTIVE_FINAL_LIST[@]}" | sort -u | while read -r test_name; do
        echo "  - ${test_name}"
    done
fi
echo "======================================================"

# For the final status, consider if the number of processed items (passed + failed + all_skipped)
# matches the total number of files that should have been processed.
EXPECTED_PROCESSED_COUNT=${TOTAL_FILES_WITH_MAIN_BLOCK}
ACTUAL_PROCESSED_IN_RESULTS_FILE=${PROCESSED_IN_LOOP_COUNT}

if [ "${ACTUAL_PROCESSED_IN_RESULTS_FILE}" -ne "${EXPECTED_PROCESSED_COUNT}" ]; then
    UNPROCESSED_COUNT=$((EXPECTED_PROCESSED_COUNT - ACTUAL_PROCESSED_IN_RESULTS_FILE))
    if [ ${UNPROCESSED_COUNT} -gt 0 ]; then
        log_error "WARNING: ${UNPROCESSED_COUNT} script(s) with a '__main__' block appear to have been MISSED (not in results file)."
    elif [ ${UNPROCESSED_COUNT} -lt 0 ]; then # Should not happen
        log_error "WARNING: More scripts processed than expected. Results file might have duplicates or an issue in counting."
    fi
fi

if [ ${FAILED_COUNT} -eq 0 ]; then
    if [ "${ACTUAL_PROCESSED_IN_RESULTS_FILE}" -eq "${EXPECTED_PROCESSED_COUNT}" ]; then
        log_success "All runnable CLI tests passed or were appropriately skipped, and all expected scripts were processed!"
        exit 0
    else
        log_error "No tests failed, but not all expected scripts were processed correctly. Please review warnings."
        exit 1
    fi
else
    log_error "Some CLI tests failed."
    exit 1
fi