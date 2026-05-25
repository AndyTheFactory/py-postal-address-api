"""Sample customer data for batch processing example."""

import sys

try:
    import openpyxl
except ImportError:
    print("openpyxl not installed. Run: pip install openpyxl")
    sys.exit(1)

# Sample data
SAMPLE_CUSTOMERS = [
    {
        "CustomerID": "CUST001",
        "Name": "Alice Müller",
        "Street": "Bahnhofstrasse",
        "HouseNumber": "1",
        "PostalCode": "8001",
        "City": "Zurich",
    },
    {
        "CustomerID": "CUST002",
        "Name": "Bob Schmidt",
        "Street": "Rue du Rhone",
        "HouseNumber": "50",
        "PostalCode": "1204",
        "City": "Geneve",
    },
    {
        "CustomerID": "CUST003",
        "Name": "Carol Keller",
        "Street": "Marktgasse",
        "HouseNumber": "5",
        "PostalCode": "3011",
        "City": "Bern",
    },
    {
        "CustomerID": "CUST004",
        "Name": "David Rossi",
        "Street": "Via Nassa",
        "HouseNumber": "2",
        "PostalCode": "6900",
        "City": "Lugano",
    },
    {
        "CustomerID": "CUST005",
        "Name": "Eva Meier",
        "Street": "Hauptstrasse",
        "HouseNumber": "100",
        "PostalCode": "4056",
        "City": "Basel",
    },
]


def create_sample_file(filepath: str = "sample_customers.xlsx") -> None:
    """Create a sample Excel file with customer addresses."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customers"

    # Write headers
    headers = ["CustomerID", "Name", "Street", "HouseNumber", "PostalCode", "City"]
    sheet.append(headers)

    # Write sample data
    for customer in SAMPLE_CUSTOMERS:
        row = [
            customer["CustomerID"],
            customer["Name"],
            customer["Street"],
            customer["HouseNumber"],
            customer["PostalCode"],
            customer["City"],
        ]
        sheet.append(row)

    # Auto-adjust column widths
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        adjusted_width = min(max_length + 2, 50)
        sheet.column_dimensions[column_letter].width = adjusted_width

    workbook.save(filepath)
    print(f"Sample file created: {filepath}")


if __name__ == "__main__":
    create_sample_file()
