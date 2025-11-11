/**
 * Grade Translation System - Frontend JavaScript Module
 * Handles grade scale selection, conversion, and display
 */

const GradeTranslation = (function() {
    'use strict';

    // API endpoints
    const API_BASE = '/grades/api';
    const ENDPOINTS = {
        scales: `${API_BASE}/scales/`,
        values: `${API_BASE}/values/`,
        translate: `${API_BASE}/translations/translate/`,
        convertGPA: `${API_BASE}/translations/convert_gpa/`,
        checkEligibility: `${API_BASE}/translations/check_eligibility/`
    };

    /**
     * Fetch all available grade scales
     * @returns {Promise<Array>} Array of grade scales
     */
    async function fetchGradeScales() {
        try {
            const response = await fetch(ENDPOINTS.scales, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch grade scales');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching grade scales:', error);
            return [];
        }
    }

    /**
     * Fetch grade values for a specific scale
     * @param {string} scaleId - UUID of the grade scale
     * @returns {Promise<Array>} Array of grade values
     */
    async function fetchGradeValues(scaleId) {
        try {
            const response = await fetch(
                `${ENDPOINTS.values}by_scale/?grade_scale=${scaleId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${getAuthToken()}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to fetch grade values');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching grade values:', error);
            return [];
        }
    }

    /**
     * Translate a grade from one scale to another
     * @param {string} sourceGradeId - UUID of source grade value
     * @param {string} targetScaleId - UUID of target grade scale
     * @returns {Promise<Object>} Translation result
     */
    async function translateGrade(sourceGradeId, targetScaleId) {
        try {
            const response = await fetch(ENDPOINTS.translate, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    source_grade_value_id: sourceGradeId,
                    target_scale_id: targetScaleId,
                    fallback_to_gpa: true
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to translate grade');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error translating grade:', error);
            return null;
        }
    }

    /**
     * Convert a numeric GPA to a grade in target scale
     * @param {number} gpaValue - GPA value (0.0-4.0)
     * @param {string} targetScaleId - UUID of target grade scale
     * @returns {Promise<Object>} Converted grade
     */
    async function convertGPAToGrade(gpaValue, targetScaleId) {
        try {
            const response = await fetch(ENDPOINTS.convertGPA, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    gpa_value: gpaValue,
                    target_scale_id: targetScaleId
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to convert GPA');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error converting GPA:', error);
            return null;
        }
    }

    /**
     * Check if a student grade meets program requirement
     * @param {number} studentGPA - Student's GPA in their scale
     * @param {string} studentScaleId - Student's grade scale ID
     * @param {number} requiredGPA - Required GPA
     * @param {string} requiredScaleId - Program's grade scale ID
     * @returns {Promise<Object>} Eligibility result
     */
    async function checkEligibility(studentGPA, studentScaleId, requiredGPA, requiredScaleId) {
        try {
            const response = await fetch(ENDPOINTS.checkEligibility, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    student_gpa: studentGPA,
                    student_scale_id: studentScaleId,
                    required_gpa: requiredGPA,
                    required_scale_id: requiredScaleId
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to check eligibility');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error checking eligibility:', error);
            return null;
        }
    }

    /**
     * Populate grade scale dropdown
     * @param {string} selectId - ID of the select element
     */
    async function populateGradeScaleDropdown(selectId) {
        const select = document.getElementById(selectId);
        if (!select) return;

        const scales = await fetchGradeScales();
        
        // Clear existing options except the first (placeholder)
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Add grade scales
        scales.forEach(scale => {
            const option = document.createElement('option');
            option.value = scale.id;
            option.textContent = `${scale.name} (${scale.country})`;
            option.dataset.code = scale.code;
            option.dataset.minValue = scale.min_value;
            option.dataset.maxValue = scale.max_value;
            select.appendChild(option);
        });
    }

    /**
     * Display GPA equivalent for a given grade
     * @param {number} gradeValue - Numeric grade value
     * @param {string} scaleId - Grade scale ID
     * @param {string} displayElementId - ID of element to show result
     */
    async function displayGPAEquivalent(gradeValue, scaleId, displayElementId) {
        if (!gradeValue || !scaleId) return;

        const displayElement = document.getElementById(displayElementId);
        if (!displayElement) return;

        displayElement.innerHTML = '<span class="text-muted">Calculating...</span>';

        try {
            const values = await fetchGradeValues(scaleId);
            const closestGrade = findClosestGrade(gradeValue, values);
            
            if (closestGrade) {
                displayElement.innerHTML = `
                    <span class="badge bg-info">
                        ${closestGrade.label} = ${closestGrade.gpa_equivalent.toFixed(2)} GPA
                    </span>
                `;
            } else {
                displayElement.innerHTML = '<span class="text-muted">N/A</span>';
            }
        } catch (error) {
            displayElement.innerHTML = '<span class="text-danger">Error</span>';
        }
    }

    /**
     * Find the closest grade value to a numeric value
     * @param {number} numericValue - The value to match
     * @param {Array} gradeValues - Array of grade values
     * @returns {Object|null} Closest grade value
     */
    function findClosestGrade(numericValue, gradeValues) {
        if (!gradeValues || gradeValues.length === 0) return null;

        let closest = null;
        let minDiff = Infinity;

        gradeValues.forEach(grade => {
            const diff = Math.abs(grade.numeric_value - numericValue);
            if (diff < minDiff) {
                minDiff = diff;
                closest = grade;
            }
        });

        return closest;
    }

    /**
     * Get authentication token from localStorage or cookie
     * @returns {string} JWT token
     */
    function getAuthToken() {
        // Try localStorage first
        let token = localStorage.getItem('access_token');
        
        // If not found, try to get from cookie
        if (!token) {
            const match = document.cookie.match(/access_token=([^;]+)/);
            token = match ? match[1] : '';
        }
        
        return token;
    }

    /**
     * Get CSRF token from cookie
     * @returns {string} CSRF token
     */
    function getCSRFToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    /**
     * Initialize grade scale selector with change handler
     * @param {string} selectId - ID of select element
     * @param {string} gradeInputId - ID of grade input element
     * @param {string} displayId - ID of display element
     */
    function initGradeScaleSelector(selectId, gradeInputId, displayId) {
        const select = document.getElementById(selectId);
        const gradeInput = document.getElementById(gradeInputId);
        
        if (!select || !gradeInput) return;

        // Populate dropdown
        populateGradeScaleDropdown(selectId);

        // Handle scale change
        select.addEventListener('change', function() {
            const scaleId = this.value;
            const gradeValue = parseFloat(gradeInput.value);
            
            if (scaleId && gradeValue) {
                displayGPAEquivalent(gradeValue, scaleId, displayId);
            }
        });

        // Handle grade input change
        gradeInput.addEventListener('input', function() {
            const scaleId = select.value;
            const gradeValue = parseFloat(this.value);
            
            if (scaleId && gradeValue) {
                displayGPAEquivalent(gradeValue, scaleId, displayId);
            }
        });
    }

    // Public API
    return {
        fetchGradeScales,
        fetchGradeValues,
        translateGrade,
        convertGPAToGrade,
        checkEligibility,
        populateGradeScaleDropdown,
        displayGPAEquivalent,
        initGradeScaleSelector,
        findClosestGrade
    };
})();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GradeTranslation;
}

