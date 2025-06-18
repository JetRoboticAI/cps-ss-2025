// src/utils/index.js

// Utility functions for smart lock system

/**
 * Format a date string or timestamp into localized string
 */
export const formatDate = (date) => {
    return new Date(date).toLocaleString();
};

/**
 * Standardized error handling
 */
export const handleError = (error) => {
    console.error("An error occurred:", error);
    return "An unexpected error occurred. Please try again.";
};

/**
 * Validate NFC tag format
 */
export const validateNFCTag = (tagId) => {
    return /^[A-F0-9]{8,}$/i.test(tagId);
};

/**
 * Format verification result message
 */
export const formatVerificationResult = (result) => {
    if (!result) return 'Verification failed';
    
    const { success, type, matchPercentage } = result;
    if (!success) return `${type} verification failed`;
    
    return matchPercentage 
        ? `${type} verified successfully (${matchPercentage}% match)`
        : `${type} verified successfully`;
};

/**
 * Generate event log entry
 */
export const createLogEntry = (type, success, message, details = {}) => {
    return {
        type,
        success,
        message,
        timestamp: new Date().toISOString(),
        ...details
    };
};

/**
 * Debounce function to prevent rapid-fire API calls
 */
export const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};