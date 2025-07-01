"""
Static file optimization script for SGII.
Minifies CSS/JS files and optimizes images.
"""

import os
import subprocess
from pathlib import Path
import shutil

# CSS Minification
CSS_MINIFY_SCRIPT = '''
/* CSS Optimization Rules */

/* 1. Combine similar rules */
.btn-primary, .btn-success, .btn-info {
    border-radius: 4px;
    font-weight: 500;
    transition: all 0.3s ease;
}

/* 2. Use CSS variables for repeated values */
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    
    --border-radius: 4px;
    --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

/* 3. Optimize selectors */
/* Instead of: .container .row .col .card .card-body .text */
/* Use: .card-body .text */

/* 4. Remove unused CSS */
/* Use tools like PurgeCSS to remove unused styles */
'''

# JavaScript Optimization
JS_OPTIMIZATION = '''
// JavaScript optimization strategies

// 1. Debounce expensive operations
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 2. Lazy load images
const lazyLoadImages = () => {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
};

// 3. Cache DOM queries
const elements = {
    form: null,
    submitBtn: null,
    resultDiv: null,
    
    init() {
        this.form = document.getElementById('exchange-form');
        this.submitBtn = document.getElementById('submit-btn');
        this.resultDiv = document.getElementById('result');
    }
};

// 4. Use event delegation
document.addEventListener('click', (e) => {
    if (e.target.matches('.delete-btn')) {
        handleDelete(e.target);
    } else if (e.target.matches('.edit-btn')) {
        handleEdit(e.target);
    }
});

// 5. Optimize loops
// Use for...of instead of forEach for better performance
// Use requestAnimationFrame for DOM updates
'''

# Webpack configuration for bundling
WEBPACK_CONFIG = '''
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
    mode: 'production',
    entry: {
        main: './SEIM/exchange/static/exchange/js/main.js',
        vendor: './SEIM/exchange/static/exchange/js/vendor.js',
    },
    output: {
        filename: '[name].[contenthash].js',
        path: path.resolve(__dirname, 'SEIM/exchange/static/exchange/dist'),
        clean: true,
    },
    optimization: {
        minimize: true,
        minimizer: [
            new TerserPlugin({
                terserOptions: {
                    compress: {
                        drop_console: true,
                        drop_debugger: true,
                    },
                },
            }),
            new CssMinimizerPlugin(),
        ],
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    priority: 10,
                },
                common: {
                    minChunks: 2,
                    priority: 5,
                    reuseExistingChunk: true,
                },
            },
        },
    },
    plugins: [
        new CompressionPlugin({
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 8192,
            minRatio: 0.8,
        }),
    ],
};
'''

# Image optimization script
IMAGE_OPTIMIZATION = '''
#!/bin/bash
# Image optimization script

# Install required tools
# pip install pillow

from PIL import Image
import os
from pathlib import Path

def optimize_images(directory):
    """Optimize all images in a directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    
    for file_path in Path(directory).rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            try:
                # Open image
                img = Image.open(file_path)
                
                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                
                # Optimize based on file type
                if file_path.suffix.lower() in {'.jpg', '.jpeg'}:
                    img.save(file_path, 'JPEG', optimize=True, quality=85)
                elif file_path.suffix.lower() == '.png':
                    img.save(file_path, 'PNG', optimize=True)
                
                print(f"Optimized: {file_path}")
                
            except Exception as e:
                print(f"Error optimizing {file_path}: {e}")

# Run optimization
if __name__ == "__main__":
    static_dir = "SEIM/exchange/static/exchange/img"
    optimize_images(static_dir)
'''

# CDN configuration
CDN_SETUP = '''
# CDN Configuration for static files

# 1. CloudFlare configuration
CLOUDFLARE_CONFIG = {
    'zone_id': 'your-zone-id',
    'api_token': 'your-api-token',
    'cache_rules': [
        {
            'match': '*.css',
            'cache_ttl': 31536000,  # 1 year
            'browser_cache_ttl': 86400,  # 1 day
        },
        {
            'match': '*.js',
            'cache_ttl': 31536000,  # 1 year
            'browser_cache_ttl': 86400,  # 1 day
        },
        {
            'match': '*.jpg|*.jpeg|*.png|*.gif|*.webp',
            'cache_ttl': 31536000,  # 1 year
            'browser_cache_ttl': 604800,  # 1 week
        },
    ],
}

# 2. Django settings for CDN
STATIC_URL = 'https://cdn.yourdomain.com/static/'
MEDIA_URL = 'https://cdn.yourdomain.com/media/'

# 3. Cache headers middleware
class CacheHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Set cache headers for static files
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000'
        elif request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=86400'
            
        return response
'''

print("Static file optimization configurations created.")
print("\nOptimization steps:")
print("1. Install optimization tools: npm install -g terser cssnano imagemin")
print("2. Run CSS minification on all CSS files")
print("3. Run JS minification on all JS files")
print("4. Optimize all images in static directories")
print("5. Configure CDN for serving static files")
print("6. Enable gzip compression in web server")
