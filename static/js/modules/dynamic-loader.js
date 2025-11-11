/**
 * SEIM Dynamic Loader Module
 * Handles code splitting, lazy loading, and bundle optimization
 */

import { SEIM_LOGGER } from './logger.js';
import { SEIM_ERROR_HANDLER } from './error-handler.js';
import SEIM_PERFORMANCE from './performance.js';

class DynamicLoader {
    constructor() {
        this.loadedModules = new Map();
        this.loadingModules = new Map();
        this.moduleConfigs = new Map();
        this.intersectionObserver = null;
        
        this.config = {
            preloadThreshold: 0.1, // Preload when element is 10% visible
            loadTimeout: 10000, // 10 seconds
            retryAttempts: 2,
            enableIntersectionObserver: true
        };
        
        this.init();
    }
    
    init() {
        this.setupIntersectionObserver();
        this.setupModuleConfigs();
        SEIM_LOGGER.info('Dynamic Loader initialized');
    }
    
    /**
     * Setup intersection observer for lazy loading
     */
    setupIntersectionObserver() {
        if (!this.config.enableIntersectionObserver || !window.IntersectionObserver) {
            SEIM_LOGGER.warn('IntersectionObserver not available, falling back to manual loading');
            return;
        }
        
        this.intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const moduleName = entry.target.dataset.module;
                        if (moduleName) {
                            this.preloadModule(moduleName);
                        }
                    }
                });
            },
            {
                threshold: this.config.preloadThreshold,
                rootMargin: '50px'
            }
        );
    }
    
    /**
     * Setup module configurations
     */
    setupModuleConfigs() {
        // Define module configurations
        const modules = {
            'applications': {
                path: '/static/js/applications.js',
                priority: 'high',
                dependencies: ['api', 'auth'],
                preload: true
            },
            'documents': {
                path: '/static/js/documents.js',
                priority: 'medium',
                dependencies: ['api', 'file-upload'],
                preload: false
            },
            'programs': {
                path: '/static/js/programs.js',
                priority: 'medium',
                dependencies: ['api'],
                preload: false
            },
            'dashboard': {
                path: '/static/js/dashboard.js',
                priority: 'high',
                dependencies: ['api', 'auth'],
                preload: true
            },
            'analytics': {
                path: '/static/js/analytics.js',
                priority: 'low',
                dependencies: ['api', 'charts'],
                preload: false
            }
        };
        
        Object.entries(modules).forEach(([name, config]) => {
            this.moduleConfigs.set(name, config);
        });
    }
    
    /**
     * Load module dynamically
     */
    async loadModule(moduleName, options = {}) {
        const {
            force = false,
            showLoading = true,
            timeout = this.config.loadTimeout
        } = options;
        
        // Check if already loaded
        if (this.loadedModules.has(moduleName) && !force) {
            SEIM_LOGGER.debug('Module already loaded', { moduleName });
            return this.loadedModules.get(moduleName);
        }
        
        // Check if currently loading
        if (this.loadingModules.has(moduleName) && !force) {
            SEIM_LOGGER.debug('Module already loading', { moduleName });
            return this.loadingModules.get(moduleName);
        }
        
        const config = this.moduleConfigs.get(moduleName);
        if (!config) {
            throw new Error(`Module configuration not found: ${moduleName}`);
        }
        
        // Show loading indicator
        if (showLoading) {
            this.showLoadingIndicator(moduleName);
        }
        
        const startTime = performance.now();
        
        // Create loading promise
        const loadPromise = this.executeModuleLoad(moduleName, config, timeout);
        
        // Store loading promise
        this.loadingModules.set(moduleName, loadPromise);
        
        try {
            const module = await loadPromise;
            const endTime = performance.now();
            
            // Track performance
            SEIM_PERFORMANCE.trackBundleLoad(moduleName, startTime, endTime, module.length || 0);
            
            // Store loaded module
            this.loadedModules.set(moduleName, module);
            this.loadingModules.delete(moduleName);
            
            // Hide loading indicator
            if (showLoading) {
                this.hideLoadingIndicator(moduleName);
            }
            
            SEIM_LOGGER.info('Module loaded successfully', { 
                moduleName, 
                duration: `${(endTime - startTime).toFixed(2)}ms` 
            });
            
            return module;
            
        } catch (error) {
            this.loadingModules.delete(moduleName);
            
            if (showLoading) {
                this.hideLoadingIndicator(moduleName);
            }
            
            SEIM_ERROR_HANDLER.handleError(error, {
                context: 'Dynamic Loader',
                moduleName,
                config
            });
            
            throw error;
        }
    }
    
    /**
     * Execute actual module loading
     */
    async executeModuleLoad(moduleName, config, timeout, retryCount = 0) {
        try {
            // Load dependencies first
            if (config.dependencies) {
                await this.loadDependencies(config.dependencies);
            }
            
            // Create script element
            const script = document.createElement('script');
            script.src = config.path;
            script.type = 'module';
            script.async = true;
            
            // Create load promise
            const loadPromise = new Promise((resolve, reject) => {
                script.onload = () => {
                    // Try to get module from global scope
                    const module = window[`SEIM_${moduleName.toUpperCase()}`] || window[moduleName];
                    if (module) {
                        resolve(module);
                    } else {
                        reject(new Error(`Module not found in global scope: ${moduleName}`));
                    }
                };
                
                script.onerror = () => {
                    reject(new Error(`Failed to load module: ${moduleName}`));
                };
            });
            
            // Add timeout
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error(`Module load timeout: ${moduleName}`)), timeout);
            });
            
            // Race between load and timeout
            const result = await Promise.race([loadPromise, timeoutPromise]);
            
            // Append script to document
            document.head.appendChild(script);
            
            return result;
            
        } catch (error) {
            // Retry logic
            if (retryCount < this.config.retryAttempts) {
                SEIM_LOGGER.warn('Retrying module load', { moduleName, retryCount: retryCount + 1 });
                
                await this.delay(1000 * Math.pow(2, retryCount));
                
                return this.executeModuleLoad(moduleName, config, timeout, retryCount + 1);
            }
            
            throw error;
        }
    }
    
    /**
     * Load module dependencies
     */
    async loadDependencies(dependencies) {
        const promises = dependencies.map(dep => {
            if (this.loadedModules.has(dep)) {
                return Promise.resolve();
            }
            
            return this.loadModule(dep, { showLoading: false });
        });
        
        await Promise.all(promises);
    }
    
    /**
     * Preload module (load without executing)
     */
    async preloadModule(moduleName) {
        if (this.loadedModules.has(moduleName) || this.loadingModules.has(moduleName)) {
            return;
        }
        
        const config = this.moduleConfigs.get(moduleName);
        if (!config || !config.preload) {
            return;
        }
        
        SEIM_LOGGER.debug('Preloading module', { moduleName });
        
        try {
            await this.loadModule(moduleName, { showLoading: false });
        } catch (error) {
            SEIM_LOGGER.warn('Failed to preload module', { moduleName, error: error.message });
        }
    }
    
    /**
     * Setup lazy loading for elements
     */
    setupLazyLoading(selector, moduleName) {
        const elements = document.querySelectorAll(selector);
        
        elements.forEach(element => {
            element.dataset.module = moduleName;
            
            if (this.intersectionObserver) {
                this.intersectionObserver.observe(element);
            }
        });
    }
    
    /**
     * Load module on demand (for event handlers)
     */
    async loadOnDemand(moduleName, callback) {
        try {
            const module = await this.loadModule(moduleName);
            
            if (typeof callback === 'function') {
                callback(module);
            }
            
            return module;
        } catch (error) {
            SEIM_LOGGER.error('Failed to load module on demand', { moduleName, error: error.message });
            throw error;
        }
    }
    
    /**
     * Show loading indicator
     */
    showLoadingIndicator(moduleName) {
        const indicator = document.createElement('div');
        indicator.className = 'seim-loading-indicator';
        indicator.id = `loading-${moduleName}`;
        indicator.innerHTML = `
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading ${moduleName}...</span>
            </div>
            <span class="ms-2">Loading ${moduleName}...</span>
        `;
        
        // Add to page
        document.body.appendChild(indicator);
        
        // Add CSS if not already present
        if (!document.getElementById('seim-loading-styles')) {
            const style = document.createElement('style');
            style.id = 'seim-loading-styles';
            style.textContent = `
                .seim-loading-indicator {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    font-size: 14px;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * Hide loading indicator
     */
    hideLoadingIndicator(moduleName) {
        const indicator = document.getElementById(`loading-${moduleName}`);
        if (indicator) {
            indicator.remove();
        }
    }
    
    /**
     * Get loading status
     */
    getLoadingStatus() {
        return {
            loaded: Array.from(this.loadedModules.keys()),
            loading: Array.from(this.loadingModules.keys()),
            available: Array.from(this.moduleConfigs.keys())
        };
    }
    
    /**
     * Unload module (for memory management)
     */
    unloadModule(moduleName) {
        this.loadedModules.delete(moduleName);
        this.loadingModules.delete(moduleName);
        
        // Remove script tag if exists
        const script = document.querySelector(`script[src*="${moduleName}"]`);
        if (script) {
            script.remove();
        }
        
        SEIM_LOGGER.info('Module unloaded', { moduleName });
    }
    
    /**
     * Clear all modules (for testing)
     */
    clear() {
        this.loadedModules.clear();
        this.loadingModules.clear();
        
        // Remove all dynamically added scripts
        document.querySelectorAll('script[src*="/static/js/"]').forEach(script => {
            script.remove();
        });
        
        SEIM_LOGGER.info('All modules cleared');
    }
    
    /**
     * Delay utility
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Create and export singleton instance
const dynamicLoader = new DynamicLoader();

// Export for use in other modules
window.SEIM_DYNAMIC_LOADER = dynamicLoader;

export default dynamicLoader; 