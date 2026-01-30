"""
Analytics Page Object for analytics and reporting.
"""

from .base_page import BasePage


class AnalyticsPage(BasePage):
    """Page object for analytics page."""
    
    # Page elements
    ANALYTICS_CONTAINER = '[data-testid="analytics"], .analytics-container'
    
    # Charts and graphs
    APPLICATIONS_CHART = '[data-testid="applications-chart"]'
    PROGRAMS_CHART = '[data-testid="programs-chart"]'
    USERS_CHART = '[data-testid="users-chart"]'
    STATUS_BREAKDOWN_CHART = '[data-testid="status-breakdown"]'
    
    # Filters
    DATE_RANGE_START = '[data-testid="date-start"], input[name="date_start"]'
    DATE_RANGE_END = '[data-testid="date-end"], input[name="date_end"]'
    FILTER_PROGRAM = '[data-testid="filter-program"], select[name="program"]'
    APPLY_FILTERS_BUTTON = '[data-testid="apply-filters"], button:has-text("Apply")'
    
    # Statistics
    TOTAL_APPLICATIONS_STAT = '[data-testid="total-applications"]'
    APPROVED_APPLICATIONS_STAT = '[data-testid="approved-applications"]'
    PENDING_APPLICATIONS_STAT = '[data-testid="pending-applications"]'
    AVERAGE_PROCESSING_TIME_STAT = '[data-testid="avg-processing-time"]'
    
    # Export
    EXPORT_PDF_BUTTON = '[data-testid="export-pdf"], button:has-text("Export PDF")'
    EXPORT_EXCEL_BUTTON = '[data-testid="export-excel"], button:has-text("Export Excel")'
    EXPORT_CSV_BUTTON = '[data-testid="export-csv"], button:has-text("Export CSV")'
    
    # Reports list
    REPORTS_TABLE = '[data-testid="reports-table"]'
    REPORT_ROW = 'tr[data-testid^="report-"]'
    
    def navigate_to_analytics(self) -> None:
        """Navigate to analytics page."""
        self.navigate('analytics/')
    
    def assert_analytics_page_loaded(self) -> None:
        """Assert that analytics page is loaded."""
        self.assert_url_contains('analytics')
        self.assert_element_visible(self.ANALYTICS_CONTAINER)
    
    def set_date_range(self, start_date: str, end_date: str) -> None:
        """
        Set date range filter.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        self.fill(self.DATE_RANGE_START, start_date)
        self.fill(self.DATE_RANGE_END, end_date)
    
    def filter_by_program(self, program_name: str) -> None:
        """
        Filter analytics by program.
        
        Args:
            program_name: Program name
        """
        self.select_option(self.FILTER_PROGRAM, program_name)
    
    def apply_filters(self) -> None:
        """Apply analytics filters."""
        self.click(self.APPLY_FILTERS_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def get_total_applications(self) -> str:
        """
        Get total applications statistic.
        
        Returns:
            Total applications count
        """
        return self.get_text(self.TOTAL_APPLICATIONS_STAT)
    
    def get_approved_applications(self) -> str:
        """
        Get approved applications statistic.
        
        Returns:
            Approved applications count
        """
        return self.get_text(self.APPROVED_APPLICATIONS_STAT)
    
    def get_pending_applications(self) -> str:
        """
        Get pending applications statistic.
        
        Returns:
            Pending applications count
        """
        return self.get_text(self.PENDING_APPLICATIONS_STAT)
    
    def export_to_pdf(self) -> None:
        """Export analytics report to PDF."""
        with self.page.expect_download() as download_info:
            self.click(self.EXPORT_PDF_BUTTON)
        return download_info.value
    
    def export_to_excel(self) -> None:
        """Export analytics report to Excel."""
        with self.page.expect_download() as download_info:
            self.click(self.EXPORT_EXCEL_BUTTON)
        return download_info.value
    
    def export_to_csv(self) -> None:
        """Export analytics report to CSV."""
        with self.page.expect_download() as download_info:
            self.click(self.EXPORT_CSV_BUTTON)
        return download_info.value
    
    def is_chart_visible(self, chart_selector: str) -> bool:
        """
        Check if a chart is visible.
        
        Args:
            chart_selector: Selector for the chart
        
        Returns:
            True if chart is visible
        """
        return self.is_visible(chart_selector, timeout=5000)

