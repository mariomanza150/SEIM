/**
 * SEIM Logger Module
 * Provides structured logging with different levels
 */

const LOG_LEVELS = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
    NONE: 4
};

class Logger {
    constructor(level = 'INFO') {
        this.level = LOG_LEVELS[level] || LOG_LEVELS.INFO;
        this.isDevelopment = process.env.NODE_ENV === 'development';
    }

    debug(message, ...args) {
        if (this.level <= LOG_LEVELS.DEBUG && this.isDevelopment) {
            console.log(`[DEBUG] ${message}`, ...args);
        }
    }

    info(message, ...args) {
        if (this.level <= LOG_LEVELS.INFO) {
            console.info(`[INFO] ${message}`, ...args);
        }
    }

    warn(message, ...args) {
        if (this.level <= LOG_LEVELS.WARN) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }

    error(message, error = null) {
        if (this.level <= LOG_LEVELS.ERROR) {
            console.error(`[ERROR] ${message}`, error);
        }
    }
}

// Create singleton instance
const logger = new Logger(process.env.LOG_LEVEL || 'INFO');

export { logger, Logger, LOG_LEVELS }; 