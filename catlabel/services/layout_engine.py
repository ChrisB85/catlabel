import html
import uuid


def _id():
    return str(uuid.uuid4())


def _escape_text(value):
    return html.escape(str(value if value is not None else ""))


def _escape_multiline(value):
    return _escape_text(value).replace("\n", "<br>")


def _html_item(x, y, w, h, markup):
    return {
        "id": _id(),
        "type": "html",
        "x": int(x),
        "y": int(y),
        "width": int(w),
        "height": int(h),
        "html": markup,
    }


def _shape_item(x, y, w, h, fill="black", shape_type="rect"):
    return {
        "id": _id(),
        "type": "shape",
        "shapeType": shape_type,
        "x": int(x),
        "y": int(y),
        "width": int(w),
        "height": int(h),
        "fill": fill,
        "stroke": "transparent",
        "strokeWidth": 0,
    }


def _text_item(
    x,
    y,
    w,
    h,
    text,
    size=40,
    weight=700,
    align="center",
    fit=True,
    color="black",
    bg_color="transparent",
    italic=False,
    underline=False,
    rotation=0,
    no_wrap=False,
    invert=False,
):
    resolved_color = "white" if invert and color == "black" else color
    resolved_bg_color = "black" if invert and bg_color == "transparent" else bg_color

    item = {
        "id": _id(),
        "type": "text",
        "text": text,
        "x": int(x),
        "y": int(y),
        "width": int(w),
        "height": int(h),
        "size": float(size),
        "weight": weight,
        "align": align,
        "fit_to_width": fit,
        "no_wrap": no_wrap,
        "color": resolved_color,
        "bgColor": resolved_bg_color,
        "italic": italic,
        "underline": underline,
        "rotation": rotation,
        "font": "RobotoCondensed.ttf",
    }
    if invert:
        item["invert"] = True
    if resolved_bg_color == "white":
        item["bg_white"] = True
    return item


def build_centered_text(width, height, params):
    text = _escape_text(params.get("text", "Text"))
    return [
        _html_item(
            0,
            0,
            width,
            height,
            f"""<div style="display:flex; width:100%; height:100%; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden;">
    <div class="auto-text" style="font-weight:900; text-align:center;">{text}</div>
  </div>
</div>""",
        )
    ]


def build_title_subtitle(width, height, params):
    title = _escape_text(params.get("title", "Title"))
    subtitle = _escape_text(params.get("subtitle", "Subtitle"))
    return [
        _html_item(
            0,
            0,
            width,
            height,
            f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:8px; gap:8px; box-sizing:border-box;">
  <div style="flex:3; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:900; text-align:center; text-transform:uppercase;">{title}</div>
  </div>
  <div style="height:4px; background:black; width:80%; margin:0 auto; flex-shrink:0;"></div>
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:600; text-align:center;">{subtitle}</div>
  </div>
</div>""",
        )
    ]


def build_price_tag(width, height, params):
    currency = _escape_text(params.get("currency_symbol", "$"))
    main = _escape_text(params.get("price_main", "19"))
    cents = _escape_text(params.get("price_cents", "99"))
    unit = _escape_text(params.get("unit", ""))
    name = _escape_text(params.get("product_name", "Product Name"))
    barcode_data = str(params.get("barcode", "123456") or "123456")
    has_barcode = bool(str(params.get("barcode", "") or "").strip())

    is_landscape = width > height
    html_w = width * 0.65 if (is_landscape and has_barcode) else width
    html_h = height * 0.65 if ((not is_landscape) and has_barcode) else height
    unit_markup = (
        f'<span style="font-size:0.4em; margin-left:4px;">{unit}</span>'
        if unit
        else ""
    )

    items = [
        _html_item(
            0,
            0,
            html_w,
            html_h,
            f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:8px; box-sizing:border-box;">
  <div style="flex:4; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:900; text-align:center; display:flex; align-items:baseline; justify-content:center;">
      <span>{currency}{main}</span>
      <span style="font-size:0.5em; vertical-align:super;">{cents}</span>
      {unit_markup}
    </div>
  </div>
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center; border-top:3px solid black; padding-top:4px;">
    <div class="auto-text" style="font-weight:700; text-align:center; text-transform:uppercase;">{name}</div>
  </div>
</div>""",
        )
    ]

    if has_barcode:
        if is_landscape:
            items.append(
                {
                    "id": _id(),
                    "type": "barcode",
                    "barcode_type": "code128",
                    "data": barcode_data,
                    "x": int(html_w + 8),
                    "y": 16,
                    "width": int(width - html_w - 24),
                    "height": int(height - 32),
                }
            )
        else:
            items.append(
                {
                    "id": _id(),
                    "type": "barcode",
                    "barcode_type": "code128",
                    "data": barcode_data,
                    "x": 16,
                    "y": int(html_h + 8),
                    "width": int(width - 32),
                    "height": int(height - html_h - 24),
                }
            )

    return items


def build_inventory_tag(width, height, params):
    code_type = str(params.get("code_type", "qrcode") or "qrcode").lower()
    resolved_code_type = code_type if code_type in ["qrcode", "barcode"] else "qrcode"
    data = str(params.get("code_data", "INV-001") or "INV-001")
    title = _escape_text(params.get("title", "Item Name"))
    dept = _escape_text(params.get("department", "WAREHOUSE"))
    sku = _escape_text(params.get("sku", "SKU-123"))

    is_landscape = width > (height * 1.3)
    items = []

    if is_landscape:
        qr_size = min(width * 0.35, height - 16)
        items.append(
            {
                "id": _id(),
                "type": resolved_code_type,
                "data": data,
                "x": 8,
                "y": int((height - qr_size) / 2),
                "width": int(qr_size),
                "height": int(qr_size),
            }
        )

        html_x = qr_size + 16
        items.append(
            _html_item(
                html_x,
                0,
                width - html_x,
                height,
                f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:8px; box-sizing:border-box; gap:4px;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; background:black; color:white; display:flex; align-items:center; justify-content:center; border-radius:4px;">
    <div class="auto-text" style="font-weight:900; letter-spacing:2px;">{dept}</div>
  </div>
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:flex-start;">
    <div class="auto-text" style="font-weight:800;">{title}</div>
  </div>
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:flex-start;">
    <div class="auto-text" style="font-weight:500; font-family:monospace;">{sku}</div>
  </div>
</div>""",
            )
        )
    else:
        dept_h = height * 0.2
        items.append(
            _html_item(
                0,
                0,
                width,
                dept_h,
                f"""<div style="display:flex; width:100%; height:100%; background:black; color:white; align-items:center; justify-content:center; box-sizing:border-box;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden;">
    <div class="auto-text" style="font-weight:900; letter-spacing:2px; text-align:center;">{dept}</div>
  </div>
</div>""",
            )
        )

        code_size = min(width * 0.6, height * 0.4)
        code_y = dept_h + 8
        items.append(
            {
                "id": _id(),
                "type": resolved_code_type,
                "data": data,
                "x": int((width - code_size) / 2),
                "y": int(code_y),
                "width": int(code_size),
                "height": int(code_size),
            }
        )

        text_y = code_y + code_size + 8
        items.append(
            _html_item(
                0,
                text_y,
                width,
                height - text_y,
                f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:4px; box-sizing:border-box; gap:4px; text-align:center;">
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:800;">{title}</div>
  </div>
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:500; font-family:monospace;">{sku}</div>
  </div>
</div>""",
            )
        )

    return items


def build_cable_flag(width, height, params):
    text = _escape_text(params.get("text", "CABLE-01"))
    is_landscape = width > height
    items = []

    html_content = f"""<div style="display:flex; width:100%; height:100%; align-items:center; justify-content:center; padding:8px; box-sizing:border-box;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:900; text-align:center;">{text}</div>
  </div>
</div>"""

    if is_landscape:
        mid_x = width / 2
        items.append(
            {
                "id": _id(),
                "type": "cut_line_indicator",
                "isVertical": True,
                "x": int(mid_x),
                "y": 0,
                "width": int(width),
                "height": int(height),
            }
        )
        items.append(_html_item(0, 0, mid_x, height, html_content))
        items.append(_html_item(mid_x, 0, width - mid_x, height, html_content))
    else:
        mid_y = height / 2
        items.append(
            {
                "id": _id(),
                "type": "cut_line_indicator",
                "isVertical": False,
                "x": 0,
                "y": int(mid_y),
                "width": int(width),
                "height": int(height),
            }
        )
        items.append(_html_item(0, 0, width, mid_y, html_content))
        items.append(_html_item(0, mid_y, width, height - mid_y, html_content))

    return items


def build_shipping_address(width, height, params):
    sender = _escape_multiline(params.get("sender", "Sender Address"))
    recipient = _escape_multiline(params.get("recipient", "Recipient Address"))
    service = _escape_text(params.get("service", "STANDARD"))

    is_landscape = width > height

    if is_landscape:
        html_markup = f"""<div style="display:flex; width:100%; height:100%; box-sizing:border-box;">
  <div style="width:15%; background:black; color:white; display:flex; align-items:center; justify-content:center; writing-mode:vertical-rl; transform:rotate(180deg);">
    <div class="auto-text" style="font-weight:900; letter-spacing:4px; padding:8px;">{service}</div>
  </div>
  <div style="flex:1; display:flex; flex-direction:column; padding:16px; gap:12px;">
    <div style="flex:1; display:flex; flex-direction:column;">
      <div style="font-size:12px; font-weight:700; margin-bottom:4px;">FROM:</div>
      <div style="flex:1; min-height:0; overflow:hidden; display:flex; align-items:flex-start; justify-content:flex-start;">
        <div class="auto-text" style="font-weight:600; text-align:left;">{sender}</div>
      </div>
    </div>
    <div style="height:2px; background:black; width:100%;"></div>
    <div style="flex:2; display:flex; flex-direction:column;">
      <div style="display:inline-block; background:black; color:white; font-weight:900; padding:4px 8px; align-self:flex-start; margin-bottom:8px; font-size:14px;">SHIP TO:</div>
      <div style="flex:1; min-height:0; overflow:hidden; display:flex; align-items:flex-start; justify-content:flex-start;">
        <div class="auto-text" style="font-weight:900; text-align:left;">{recipient}</div>
      </div>
    </div>
  </div>
</div>"""
    else:
        html_markup = f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; box-sizing:border-box;">
  <div style="height:12%; background:black; color:white; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:900; letter-spacing:4px; padding:4px;">{service}</div>
  </div>
  <div style="flex:1; display:flex; flex-direction:column; padding:12px; gap:8px;">
    <div style="flex:1; display:flex; flex-direction:column;">
      <div style="font-size:12px; font-weight:700; margin-bottom:2px;">FROM:</div>
      <div style="flex:1; min-height:0; overflow:hidden; display:flex; align-items:flex-start; justify-content:flex-start;">
        <div class="auto-text" style="font-weight:600; text-align:left;">{sender}</div>
      </div>
    </div>
    <div style="height:2px; background:black; width:100%;"></div>
    <div style="flex:2; display:flex; flex-direction:column;">
      <div style="display:inline-block; background:black; color:white; font-weight:900; padding:4px 8px; align-self:flex-start; margin-bottom:8px; font-size:14px;">SHIP TO:</div>
      <div style="flex:1; min-height:0; overflow:hidden; display:flex; align-items:flex-start; justify-content:flex-start;">
        <div class="auto-text" style="font-weight:900; text-align:left;">{recipient}</div>
      </div>
    </div>
  </div>
</div>"""

    return [_html_item(0, 0, width, height, html_markup)]


def build_warning_banner(width, height, params):
    text = _escape_text(params.get("text", "WARNING"))
    return [
        _html_item(
            0,
            0,
            width,
            height,
            f"""<div style="display:flex; width:100%; height:100%; background:black; color:white; align-items:center; justify-content:center; padding:12px; box-sizing:border-box;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; border:4px solid white; display:flex; align-items:center; justify-content:center; padding:4px;">
    <div class="auto-text" style="font-weight:900; text-align:center; text-transform:uppercase; letter-spacing:2px;">{text}</div>
  </div>
</div>""",
        )
    ]


def build_sale_tag(width, height, params):
    currency = _escape_text(params.get("currency", "$"))
    old_price = f"{currency}{_escape_text(params.get('old_price', '29.99'))}"
    new_price = f"{currency}{_escape_text(params.get('new_price', '19.99'))}"
    product = _escape_text(params.get("product_name", "Sale Item"))

    is_landscape = width > height

    if is_landscape:
        html_markup = f"""<div style="display:flex; width:100%; height:100%; box-sizing:border-box;">
  <div style="flex:1; padding:12px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;">
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; width:100%; display:flex; align-items:flex-end;">
      <div class="auto-text" style="font-weight:700;">{product}</div>
    </div>
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; width:100%; display:flex; align-items:flex-start; margin-top:4px;">
      <div class="auto-text" style="font-weight:900; text-decoration:line-through; color:#666;">{old_price}</div>
    </div>
  </div>
  <div style="flex:1; background:black; color:white; display:flex; align-items:center; justify-content:center; padding:16px;">
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
      <div class="auto-text" style="font-weight:900;">{new_price}</div>
    </div>
  </div>
</div>"""
    else:
        html_markup = f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; box-sizing:border-box;">
  <div style="flex:1; padding:8px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; width:100%; display:flex; align-items:flex-end; justify-content:center;">
      <div class="auto-text" style="font-weight:700;">{product}</div>
    </div>
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; width:100%; display:flex; align-items:flex-start; justify-content:center; margin-top:4px;">
      <div class="auto-text" style="font-weight:900; text-decoration:line-through; color:#666;">{old_price}</div>
    </div>
  </div>
  <div style="flex:1; background:black; color:white; display:flex; align-items:center; justify-content:center; padding:12px;">
    <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
      <div class="auto-text" style="font-weight:900;">{new_price}</div>
    </div>
  </div>
</div>"""

    return [_html_item(0, 0, width, height, html_markup)]


def build_asset_tag(width, height, params):
    asset_id = _escape_text(params.get("asset_id", "AST-0001"))
    dept = _escape_text(params.get("department", "IT DEPT"))
    desc = _escape_text(params.get("description", "Laptop Computer"))

    is_landscape = width > height
    header_h = height * 0.25 if is_landscape else height * 0.15

    items = [
        _html_item(
            0,
            0,
            width,
            header_h,
            f"""<div style="display:flex; width:100%; height:100%; background:black; color:white; align-items:center; justify-content:center;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden;">
    <div class="auto-text" style="font-weight:900; letter-spacing:2px; text-align:center;">{dept}</div>
  </div>
</div>""",
        )
    ]

    if is_landscape:
        qr_size = min(width * 0.35, height - header_h - 16)
        qr_y = header_h + ((height - header_h - qr_size) / 2)
        items.append(
            {
                "id": _id(),
                "type": "qrcode",
                "data": asset_id,
                "x": 8,
                "y": int(qr_y),
                "width": int(qr_size),
                "height": int(qr_size),
            }
        )

        html_x = qr_size + 16
        items.append(
            _html_item(
                html_x,
                header_h,
                width - html_x,
                height - header_h,
                f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:8px; box-sizing:border-box; gap:4px;">
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:flex-end;">
    <div class="auto-text" style="font-weight:900;">{asset_id}</div>
  </div>
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:flex-start;">
    <div class="auto-text" style="font-weight:500; font-style:italic;">{desc}</div>
  </div>
</div>""",
            )
        )
    else:
        qr_size = min(width * 0.6, height * 0.4)
        qr_x = (width - qr_size) / 2
        qr_y = header_h + 8
        items.append(
            {
                "id": _id(),
                "type": "qrcode",
                "data": asset_id,
                "x": int(qr_x),
                "y": int(qr_y),
                "width": int(qr_size),
                "height": int(qr_size),
            }
        )

        text_y = qr_y + qr_size + 8
        items.append(
            _html_item(
                0,
                text_y,
                width,
                height - text_y,
                f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:4px; box-sizing:border-box; text-align:center;">
  <div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:900;">{asset_id}</div>
  </div>
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <div class="auto-text" style="font-weight:500; font-style:italic;">{desc}</div>
  </div>
</div>""",
            )
        )

    return items


def build_spice_jar(width, height, params):
    style = str(params.get("style", "jar_apothecary") or "jar_apothecary").strip()
    if style not in {"jar_apothecary", "jar_farmhouse"}:
        style = "jar_apothecary"

    return [
        {
            "id": _id(),
            "type": "label_template",
            "template_id": style,
            "text": str(params.get("text", "PREMIUM") or "PREMIUM"),
            "title": str(params.get("title", "Basil") or "Basil"),
            "subtitle": str(params.get("subtitle", "Sweet & Aromatic") or "Sweet & Aromatic"),
            "x": 0,
            "y": 0,
            "width": int(width),
            "height": int(height),
        }
    ]


def build_icon_text(width, height, params):
    text = _escape_text(params.get("text", "Label"))
    direction = str(params.get("direction", "row") or "row")
    icon_src = params.get("icon_src")
    if not icon_src:
        icon_src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTIgMiAxNS4wOSA4LjI2IDIyIDkuMjcgMTcgMTQuMTQgMTguMTggMjEuMDIgMTIgMTcuNzcgNS44MiAyMS4wMiA3IDE0LjE0IDIgOS4yNyA4LjkxIDguMjYgMTIgMiI+PC9wb2x5Z29uPjwvc3ZnPg=="

    flex_dir = "row" if direction == "row" else "column"
    align = "flex-start" if direction == "row" else "center"
    text_align = "left" if direction == "row" else "center"
    img_style = (
        "height:100%; max-width:40%; object-fit:contain;"
        if direction == "row"
        else "width:100%; max-height:40%; object-fit:contain;"
    )
    escaped_icon_src = _escape_text(icon_src)

    html_markup = f"""<div style="display:flex; flex-direction:{flex_dir}; width:100%; height:100%; padding:12px; box-sizing:border-box; align-items:center; justify-content:center; gap:12px;">
  <img src="{escaped_icon_src}" style="{img_style} flex-shrink:0;" />
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:{align}; justify-content:center; width:100%;">
    <div class="auto-text" style="font-weight:900; text-align:{text_align};">{text}</div>
  </div>
</div>"""

    return [_html_item(0, 0, width, height, html_markup)]


def build_qr_text(width, height, params):
    text = _escape_text(str(params.get("text", "Scan Me") or "Scan Me").strip())
    data = str(params.get("data", "https://catlabel.com") or "https://catlabel.com")

    is_landscape = width > height
    items = []

    if is_landscape:
        qr_size = min(width * 0.4, height - 16)
        items.append(
            {
                "id": _id(),
                "type": "qrcode",
                "data": data,
                "x": 8,
                "y": int((height - qr_size) / 2),
                "width": int(qr_size),
                "height": int(qr_size),
            }
        )
        items.append(
            _html_item(
                qr_size + 16,
                0,
                width - qr_size - 16,
                height,
                f"""<div style="display:flex; width:100%; height:100%; align-items:center; justify-content:center;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden;">
    <div class="auto-text" style="font-weight:900; text-align:center;">{text}</div>
  </div>
</div>""",
            )
        )
    else:
        qr_size = min(width - 16, height * 0.6)
        qr_x = (width - qr_size) / 2
        items.append(
            {
                "id": _id(),
                "type": "qrcode",
                "data": data,
                "x": int(qr_x),
                "y": 8,
                "width": int(qr_size),
                "height": int(qr_size),
            }
        )
        text_y = qr_size + 16
        items.append(
            _html_item(
                8,
                text_y,
                width - 16,
                height - text_y,
                f"""<div style="display:flex; width:100%; height:100%; align-items:center; justify-content:center;">
  <div style="flex:1; min-width:0; min-height:0; overflow:hidden;">
    <div class="auto-text" style="font-weight:900; text-align:center;">{text}</div>
  </div>
</div>""",
            )
        )

    return items


def build_expiration_date(width, height, params):
    product = _escape_text(str(params.get("product_name", "") or "").strip())
    made = _escape_text(str(params.get("made_date", "") or "").strip())
    exp = _escape_text(str(params.get("exp_date", "2025-12-31") or "2025-12-31").strip())

    html_parts = []
    if product:
        html_parts.append(
            f"""<div style="flex:2; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:flex-end; justify-content:center;">
  <div class="auto-text" style="font-weight:800; text-transform:uppercase;">{product}</div>
</div>"""
        )
    if made:
        html_parts.append(
            f"""<div style="flex:1; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center; margin-top:4px;">
  <div class="auto-text" style="font-weight:500;">MFG: {made}</div>
</div>"""
        )
    if exp:
        html_parts.append(
            f"""<div style="flex:3; min-width:0; min-height:0; overflow:hidden; display:flex; align-items:center; justify-content:center; margin-top:4px; border:2px solid black; padding:4px; border-radius:4px;">
  <div class="auto-text" style="font-weight:900;">EXP: {exp}</div>
</div>"""
        )

    if not html_parts:
        return []

    return [
        _html_item(
            0,
            0,
            width,
            height,
            f"""<div style="display:flex; flex-direction:column; width:100%; height:100%; padding:12px; box-sizing:border-box; text-align:center;">
  {''.join(html_parts)}
</div>""",
        )
    ]


TEMPLATE_REGISTRY = {
    "centered_text": build_centered_text,
    "title_subtitle": build_title_subtitle,
    "icon_text": build_icon_text,
    "qr_text": build_qr_text,
    "price_tag": build_price_tag,
    "inventory_tag": build_inventory_tag,
    "cable_flag": build_cable_flag,
    "shipping_address": build_shipping_address,
    "warning_banner": build_warning_banner,
    "sale_tag": build_sale_tag,
    "asset_tag": build_asset_tag,
    "spice_jar": build_spice_jar,
    "expiration_date": build_expiration_date,
}


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


def generate_template_items(template_id: str, width: int, height: int, params: dict):
    """Executes the requested template and returns the list of layout items."""
    generator = TEMPLATE_REGISTRY.get(template_id)
    if not generator:
        return None
    return generator(width, height, params)
