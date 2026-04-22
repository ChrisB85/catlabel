TEMPLATE_METADATA = [
    {
        "id": "centered_text",
        "category": "Layout",
        "name": "Centered Text",
        "description": "A single, perfectly auto-scaling text block.",
        "fields": [{"name": "text", "label": "Main Text", "type": "textarea"}],
    },
    {
        "id": "title_subtitle",
        "category": "Layout",
        "name": "Title & Subtitle",
        "description": "Stacked text with a large bold title.",
        "fields": [
            {"name": "title", "label": "Title", "type": "text"},
            {"name": "subtitle", "label": "Subtitle", "type": "text"},
        ],
    },
    {
        "id": "icon_text",
        "category": "Layout",
        "name": "Icon + Text",
        "description": "A clean icon next to your text.",
        "fields": [
            {"name": "icon_src", "label": "Icon", "type": "icon"},
            {"name": "text", "label": "Text", "type": "text", "default": "Label"},
            {
                "name": "direction",
                "label": "Layout",
                "type": "select",
                "options": [
                    {"label": "Row (Left to Right)", "value": "row"},
                    {"label": "Column (Top to Bottom)", "value": "col"},
                ],
                "default": "row",
            },
        ],
    },
    {
        "id": "qr_text",
        "category": "Layout",
        "name": "QR Code + Text",
        "description": "A QR code with adjacent text.",
        "fields": [
            {"name": "data", "label": "QR Data", "type": "text", "default": "https://google.com"},
            {"name": "text", "label": "Text", "type": "textarea", "default": "Scan Me"},
        ],
    },
    {
        "id": "price_tag",
        "category": "Dedicated",
        "name": "Price Tag with Barcode",
        "description": "Retail price tag. Automatically adapts to square or wide labels.",
        "fields": [
            {"name": "currency_symbol", "label": "Currency Symbol", "type": "text", "default": "$"},
            {"name": "price_main", "label": "Main Price", "type": "text", "default": "19"},
            {"name": "price_cents", "label": "Cents", "type": "text", "default": "99"},
            {"name": "unit", "label": "Unit (e.g. /ea)", "type": "text", "default": ""},
            {"name": "product_name", "label": "Product Name", "type": "text", "default": "Product Name"},
            {"name": "barcode", "label": "Barcode (Leave blank to omit)", "type": "text", "default": "123456789"},
        ],
    },
    {
        "id": "inventory_tag",
        "category": "Dedicated",
        "name": "Modern Inventory Tag",
        "description": "Professional asset tag with inverted department header and QR/Barcode.",
        "fields": [
            {"name": "department", "label": "Department / Category", "type": "text", "default": "WAREHOUSE"},
            {"name": "title", "label": "Item Name", "type": "text", "default": "Item Name"},
            {"name": "sku", "label": "SKU / Subtext", "type": "text", "default": "SKU-123"},
            {"name": "code_type", "label": "Code Type (qrcode or barcode)", "type": "text", "default": "qrcode"},
            {"name": "code_data", "label": "Code Data", "type": "text", "default": "INV-001"},
        ],
    },
    {
        "id": "cable_flag",
        "category": "Dedicated",
        "name": "Cable Flag",
        "description": "Fold-over tag with a dashed center line. Repeats text on both sides.",
        "fields": [{"name": "text", "label": "Cable ID / Text", "type": "text"}],
    },
    {
        "id": "shipping_address",
        "category": "Dedicated",
        "name": "Shipping Address",
        "description": "Professional shipping label with service banner and sender/recipient blocks.",
        "fields": [
            {"name": "service", "label": "Service Type (e.g. PRIORITY, STANDARD)", "type": "text", "default": "PRIORITY"},
            {"name": "sender", "label": "Sender Address", "type": "textarea"},
            {"name": "recipient", "label": "Recipient Address", "type": "textarea"},
        ],
    },
    {
        "id": "warning_banner",
        "category": "Dedicated",
        "name": "Warning Banner",
        "description": "Inverted black background with bold white text.",
        "fields": [
            {"name": "text", "label": "Warning Text", "type": "text", "default": "FRAGILE"}
        ],
    },
    {
        "id": "sale_tag",
        "category": "Dedicated",
        "name": "Retail Sale Tag",
        "description": "High contrast inverted price box.",
        "fields": [
            {"name": "product_name", "label": "Product", "type": "text"},
            {"name": "old_price", "label": "Old Price", "type": "text"},
            {"name": "new_price", "label": "New Price", "type": "text"},
            {"name": "currency", "label": "Currency", "type": "text", "default": "$"},
        ],
    },
    {
        "id": "asset_tag",
        "category": "Dedicated",
        "name": "IT Asset Tag",
        "description": "Header bar, QR code, and details.",
        "fields": [
            {"name": "department", "label": "Department", "type": "text"},
            {"name": "asset_id", "label": "Asset ID", "type": "text"},
            {"name": "description", "label": "Description", "type": "text"},
        ],
    },
    {
        "id": "spice_jar",
        "category": "Dedicated",
        "name": "Pantry / Spice Jar",
        "description": "Elegant typography for home organization.",
        "fields": [
            {
                "name": "style",
                "label": "Design Style",
                "type": "select",
                "options": [
                    {"label": "Apothecary (Classic)", "value": "jar_apothecary"},
                    {"label": "Farmhouse (Stripes & Clean)", "value": "jar_farmhouse"},
                ],
                "default": "jar_apothecary",
            },
            {"name": "title", "label": "Main Label", "type": "text"},
            {"name": "subtitle", "label": "Subtitle / Details", "type": "text"},
            {"name": "text", "label": "Top Text (e.g. Premium)", "type": "text", "default": "PREMIUM"},
        ],
    },
    {
        "id": "expiration_date",
        "category": "Dedicated",
        "name": "Expiration / Batch Date",
        "description": "Prominent expiration date, optionally with product name and manufacturing date.",
        "fields": [
            {"name": "product_name", "label": "Product Name (Optional)", "type": "text", "default": ""},
            {"name": "exp_date", "label": "Expiration Date", "type": "text", "default": "2025-12-31"},
            {"name": "made_date", "label": "Mfg / Made On (Optional)", "type": "text", "default": ""},
        ],
    },
]

