// Default thresholds (fallback values)
const DEFAULT_THRESHOLDS = {
  error_rate_success_threshold: 1.0,
  error_rate_warning_threshold: 5.0,
  latency_success_threshold: 500,
  latency_warning_threshold: 1000
};

// Global threshold store
let currentThresholds = { ...DEFAULT_THRESHOLDS };

/**
 * Update the global thresholds with values from the API
 * @param {Object} thresholds - Threshold values from the API
 */
export const updateThresholds = (thresholds) => {
  currentThresholds = {
    ...DEFAULT_THRESHOLDS,
    ...thresholds
  };
};

/**
 * Get current threshold values
 * @returns {Object} - Current threshold values
 */
export const getCurrentThresholds = () => {
  return { ...currentThresholds };
};

/**
 * Get the appropriate color for an error rate based on thresholds
 * @param {number} errorRate - The error rate as a percentage (0-100)
 * @returns {string} - The MUI color string ('success.main', 'warning.main', or 'error.main')
 */
export const getErrorRateColor = (errorRate) => {
  if (errorRate > currentThresholds.error_rate_warning_threshold) {
    return 'error.main';
  } else if (errorRate > currentThresholds.error_rate_success_threshold) {
    return 'warning.main';
  } else {
    return 'success.main';
  }
};

/**
 * Get the status level for an error rate
 * @param {number} errorRate - The error rate as a percentage (0-100)
 * @returns {string} - The status level ('success', 'warning', or 'error')
 */
export const getErrorRateStatus = (errorRate) => {
  if (errorRate > currentThresholds.error_rate_warning_threshold) {
    return 'error';
  } else if (errorRate > currentThresholds.error_rate_success_threshold) {
    return 'warning';
  } else {
    return 'success';
  }
};

/**
 * Get the appropriate color for latency based on thresholds
 * @param {number} latencyMs - The latency in milliseconds
 * @returns {string} - The MUI color string ('success.main', 'warning.main', or 'error.main')
 */
export const getLatencyColor = (latencyMs) => {
  if (latencyMs > currentThresholds.latency_warning_threshold) {
    return 'error.main';
  } else if (latencyMs > currentThresholds.latency_success_threshold) {
    return 'warning.main';
  } else {
    return 'success.main';
  }
};

/**
 * Get the status level for latency
 * @param {number} latencyMs - The latency in milliseconds
 * @returns {string} - The status level ('success', 'warning', or 'error')
 */
export const getLatencyStatus = (latencyMs) => {
  if (latencyMs > currentThresholds.latency_warning_threshold) {
    return 'error';
  } else if (latencyMs > currentThresholds.latency_success_threshold) {
    return 'warning';
  } else {
    return 'success';
  }
};
