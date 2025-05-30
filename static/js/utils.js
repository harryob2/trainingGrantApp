/**
 * Shared utility functions for the training form application
 */

/**
 * Parse currency value from string, removing currency symbols and formatting
 * @param {string|number} val - The value to parse
 * @returns {number} - The parsed numeric value
 */
function parseCurrency(val) {
    if (!val) return 0;
    // Remove currency symbols, thousands separators, etc., keep decimal point and sign
    return parseFloat(val.toString().replace(/[^0-9.-]+/g, "")) || 0;
}

/**
 * Check if an element is really visible (not just display:block)
 * @param {HTMLElement} element - The element to check
 * @returns {boolean} - True if element is visible
 */
function isReallyVisible(element) {
    if (!element) return false;
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
}

// Make functions available globally
window.parseCurrency = parseCurrency;
window.isReallyVisible = isReallyVisible; 