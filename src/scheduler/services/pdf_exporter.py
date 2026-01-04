"""PDF export service for schedule grids."""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch

from scheduler.domain.models import Course


class SchedulePDFExporter:
    """Generate PDF schedules."""
    
    def generate_weekly_grid(self, courses: list[Course]) -> BytesIO:
        """Generate PDF of weekly schedule grid.
        
        Args:
            courses: List of all scheduled courses
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build grid data
        grid_data = self._build_grid_data(courses)
        
        # Create table
        table = Table(grid_data, colWidths=[0.8*inch, 1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            # Period column styling
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            # Grid and padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Build PDF
        story = [table]
        doc.build(story)
        
        buffer.seek(0)
        return buffer
    
    def _build_grid_data(self, courses: list[Course]) -> list[list[str]]:
        """Build 2D grid data structure.
        
        Args:
            courses: List of courses to organize
            
        Returns:
            2D list of strings for PDF table
        """
        # Header row
        data = [['Period', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']]
        
        # Organize courses by timeslot
        grid = {}
        for course in courses:
            if course.weekday and course.period:
                key = (course.period, course.weekday)
                if key not in grid:
                    grid[key] = []
                grid[key].append(f"{course.id}\n{course.name}")
        
        # Build rows (12 periods)
        for period in range(1, 13):
            row = [f"P{period}"]
            for day in range(1, 6):  # Mon-Fri
                cell_courses = grid.get((period, day), [])
                row.append("\n".join(cell_courses) if cell_courses else "")
            data.append(row)
        
        return data
