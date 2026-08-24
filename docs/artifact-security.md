# 🛡️ Artifact Viewer Security & Isolation Strategy

## Overview

The Lenny Growth Assistant enables users to generate Markdown documents or complete HTML/CSS artifacts during conversation. Because generated HTML originates from LLM output, it must be treated as **untrusted content**.

This document details the multi-layered security isolation strategy implemented to prevent Cross-Site Scripting (XSS), data exfiltration, and unauthorized DOM access.

---

## Security Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Web Application                            │
│  ┌────────────────────────┐         ┌───────────────────────────────┐  │
│  │  Main App Window       │         │  Artifact Viewer Side Panel   │  │
│  │  (React + Zustand)     │         │  ┌─────────────────────────┐ │  │
│  │                        │         │  │ 1. DOMPurify Sanitizer  │ │  │
│  │                        │         │  └───────────┬─────────────┘ │  │
│  │                        │         │              │               │  │
│  │                        │         │  ┌───────────▼─────────────┐ │  │
│  │                        │         │  │ 2. Sandboxed Iframe    │ │  │
│  │                        │         │  │    (no scripts)         │ │  │
│  │                        │         │  └─────────────────────────┘ │  │
│  └────────────────────────┘         └───────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. DOMPurify HTML Sanitization

Before any generated HTML string is injected into the viewer iframe, it passes through `DOMPurify.sanitize()` with strict allowlists.

### Allowed Elements
- **Layout & Structure**: `div`, `span`, `p`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `section`, `article`, `header`, `footer`, `main`
- **Lists**: `ul`, `ol`, `li`, `dl`, `dt`, `dd`
- **Text Formatting**: `b`, `i`, `strong`, `em`, `mark`, `small`, `sub`, `sup`, `code`, `pre`, `blockquote`
- **Tables**: `table`, `tr`, `td`, `th`, `thead`, `tbody`, `tfoot`, `caption`
- **Styling**: `style` (inline CSS declarations for responsive styling)

### Explicitly Blocked & Stripped Elements
- ❌ `<script>` tags (JavaScript execution blocked)
- ❌ `<iframe>`, `<embed>`, `<object>` (nested frame insertion blocked)
- ❌ `<form>`, `<input>`, `<button>`, `<textarea>` (form hijack / phishing blocked)
- ❌ `<a>` with `javascript:` protocol (URL execution blocked)
- ❌ Inline event handlers (`onclick`, `onerror`, `onload`, `onmouseover`, etc.)

---

## 2. Sandboxed Iframe Isolation

Sanitized HTML is rendered inside an `<iframe>` container with explicit `sandbox` restriction attributes:

```html
<iframe
  title="Artifact Viewer"
  sandbox="allow-same-origin"
  srcdoc={sanitizedHtml}
/>
```

### What `sandbox="allow-same-origin"` Permits:
- ✅ Inline CSS styling and layout rendering
- ✅ SVG rendering
- ✅ Native browser typography and layout reflow

### What is Strictly Blocked by Omitting `allow-scripts` & `allow-top-navigation`:
- ❌ **JavaScript Execution**: No script execution, even if a tag escaped sanitization
- ❌ **Top-level Navigation**: Cannot redirect the user's parent browser window (`window.top.location`)
- ❌ **Popup Windows**: Cannot open popup windows (`window.open`)
- ❌ **Form Submission**: Cannot submit forms or transmit credentials to external servers
- ❌ **Storage Access**: Cannot access parent application `localStorage`, `sessionStorage`, or cookies

---

## 3. Backend Content Security Policy (CSP) Headers

Artifact API endpoints serve response headers enforcing strict Content Security Policies:

```http
Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; img-src data:; frame-ancestors 'self';
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
```

---

## Summary Matrix

| Threat Vector | Mitigation Technique | Permitted / Blocked |
| --- | --- | --- |
| **XSS Injection (`<script>`)** | DOMPurify + Iframe `sandbox` (no `allow-scripts`) | ❌ BLOCKED |
| **Inline Event Handlers (`onerror`)** | DOMPurify attribute stripping | ❌ BLOCKED |
| **Parent Window Hijack** | Omission of `allow-top-navigation` sandbox flag | ❌ BLOCKED |
| **Phishing Forms (`<form>`)** | DOMPurify tag removal | ❌ BLOCKED |
| **Local Storage / Cookie Theft** | Sandboxed document origin isolation | ❌ BLOCKED |
| **Inline CSS Layout Styling** | Allowed in DOMPurify + sandbox | ✅ PERMITTED |
| **Markdown / HTML Document Export** | Sanitized raw text copy & file download | ✅ PERMITTED |
