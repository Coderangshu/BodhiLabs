#!/usr/bin/python3
import os, json, re
import tinycss2
import webcolors

STYLE_FILE = "/home/labDirectory/tables/style.css"
EXPECTED_FILE = os.path.join(os.path.dirname(__file__), "tables.json")

def make_entry(selector, property_name, status, message):
    return {
        "testid": f"CSS/{selector} - {property_name}",
        "status": "success" if status else "failure",
        "score": 1 if status else 0,
        "maximum marks": 1,
        "message": message
    }

def parse_student_styles(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    selector_to_props = {}
    for rule in rules:
        if rule.type != "qualified-rule":
            continue
        selector = tinycss2.serialize(rule.prelude).strip()
        declarations = tinycss2.parse_declaration_list(rule.content)
        props = {}
        for decl in declarations:
            if decl.type == "declaration":
                props[decl.name.strip()] = tinycss2.serialize(decl.value).strip()
        selector_to_props[selector] = props
    return selector_to_props

def normalize_color(value):
    value = value.strip().lower()
    try:
        rgb = webcolors.name_to_rgb(value)
    except ValueError:
        try:
            rgb = webcolors.hex_to_rgb(value)
        except ValueError:
            try:
                if value.startswith("rgb("):
                    value = value.replace(" ", "").lower()
                    parts = value[4:-1].split(",")
                    rgb = tuple(int(p) for p in parts)
                else:
                    return value
            except Exception:
                return value
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

def normalize_color_in_value(value):
    if not value:
        return value
    pattern = r"(#[0-9a-fA-F]{3,6}|\brgb\s*\([^)]*\)|\b[a-zA-Z]+\b)"
    def repl(match):
        token = match.group(0)
        try:
            return normalize_color(token)
        except Exception:
            return token
    return re.sub(pattern, repl, value)

with open(EXPECTED_FILE) as f:
    expected_styles = json.load(f)

results = {"data": []}

try:
    student_styles = parse_student_styles(STYLE_FILE)

    for selector, expected_props in expected_styles.items():
        student_props = student_styles.get(selector, {})
        for prop, expected_val in expected_props.items():
            student_val = student_props.get(prop)
            if student_val:
                student_val = normalize_color_in_value(student_val)
                expected_val = normalize_color_in_value(expected_val)
            if student_val == expected_val:
                msg = f"✔ {selector} sets '{prop}' correctly"
                results["data"].append(make_entry(selector, prop, True, msg))
            else:
                msg = f"✘ Expected '{expected_val}' but got '{student_val}'" if student_val else "✘ Property missing"
                results["data"].append(make_entry(selector, prop, False, msg))

except Exception as e:
    results["data"].append({
        "testid": "CSS/Error",
        "status": "failure",
        "score": 0,
        "maximum marks": 1,
        "message": f"Autograder crashed: {e}"
    })

eval_path = os.path.join(os.path.dirname(__file__), "../.evaluationScripts/evaluate.json")
with open(eval_path, "w") as f:
    json.dump(results, f, indent=4)
