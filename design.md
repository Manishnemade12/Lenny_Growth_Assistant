# 🎨 Design Document

## The Lenny Growth Assistant — UI/UX Design

---

## 1. Design Philosophy

### Core Principles

1. **Clarity Over Cleverness**: Every interaction should be immediately understandable. Users are product managers, not prompt engineers — the UI should hide complexity while exposing capability.

2. **Grounded Trust**: Visual design reinforces that answers come from real sources. Citations are always visible, not hidden. The source of truth (transcript data) is always one click away.

3. **Professional Warmth**: The design should feel like a premium internal tool — clean, modern, and professional — but not cold. Warm neutral tones with accent colors that feel inviting.

4. **Progressive Disclosure**: Show the most important information first. Details (source transcripts, metadata, settings) are accessible but don't clutter the primary experience.

5. **Responsive First**: The layout must work seamlessly from desktop (where most PM work happens) down to tablet (for meetings and quick lookups).

---

## 2. Color System

### Light Theme (Default)

```css
:root {
  /* Background */
  --bg-primary: #FAFAFA;          /* Main background */
  --bg-secondary: #FFFFFF;         /* Cards, panels */
  --bg-tertiary: #F5F5F5;          /* Sidebar, subtle areas */
  --bg-hover: #F0F0F0;             /* Hover states */
  
  /* Text */
  --text-primary: #1A1A2E;         /* Headings, primary content */
  --text-secondary: #4A4A68;       /* Body text */
  --text-tertiary: #8A8AA3;        /* Muted text, timestamps */
  --text-inverse: #FFFFFF;          /* Text on dark backgrounds */
  
  /* Accent — Warm Indigo */
  --accent-primary: #6366F1;        /* Primary actions, links */
  --accent-hover: #4F46E5;          /* Hover state */
  --accent-light: #EEF2FF;          /* Accent backgrounds */
  --accent-muted: #C7D2FE;          /* Borders, subtle accents */
  
  /* Semantic */
  --success: #10B981;               /* Connected, healthy */
  --warning: #F59E0B;               /* Degraded, slow */
  --error: #EF4444;                 /* Error, disconnected */
  --info: #3B82F6;                  /* Informational */
  
  /* Surfaces */
  --border: #E5E7EB;                /* Borders */
  --shadow: rgba(0, 0, 0, 0.05);   /* Subtle shadows */
  --shadow-lg: rgba(0, 0, 0, 0.1); /* Elevated shadows */
  
  /* Chat-specific */
  --user-bubble: #6366F1;           /* User message background */
  --user-text: #FFFFFF;             /* User message text */
  --assistant-bubble: #FFFFFF;      /* Assistant message background */
  --assistant-text: #1A1A2E;        /* Assistant message text */
  --citation-bg: #FEF3C7;          /* Source citation highlight */
  --citation-border: #F59E0B;       /* Citation accent */
}
```

### Dark Theme

```css
[data-theme="dark"] {
  --bg-primary: #0F0F1A;
  --bg-secondary: #1A1A2E;
  --bg-tertiary: #16162A;
  --bg-hover: #252540;
  
  --text-primary: #F0F0F5;
  --text-secondary: #B0B0C8;
  --text-tertiary: #6A6A88;
  --text-inverse: #0F0F1A;
  
  --accent-primary: #818CF8;
  --accent-hover: #6366F1;
  --accent-light: #1E1B4B;
  --accent-muted: #3730A3;
  
  --border: #2A2A45;
  --shadow: rgba(0, 0, 0, 0.3);
  --shadow-lg: rgba(0, 0, 0, 0.5);
  
  --user-bubble: #4F46E5;
  --assistant-bubble: #1A1A2E;
  --assistant-text: #F0F0F5;
  --citation-bg: #451A03;
  --citation-border: #D97706;
}
```

---

## 3. Typography

```css
/* Font Stack */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  
  /* Type Scale */
  --text-xs: 0.75rem;     /* 12px — metadata, timestamps */
  --text-sm: 0.875rem;    /* 14px — secondary text, captions */
  --text-base: 1rem;      /* 16px — body text, messages */
  --text-lg: 1.125rem;    /* 18px — subheadings */
  --text-xl: 1.25rem;     /* 20px — section headings */
  --text-2xl: 1.5rem;     /* 24px — page titles */
  --text-3xl: 1.875rem;   /* 30px — hero text */
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

---

## 4. Information Architecture

### 4.1 Layout Structure

```
┌────────────────────────────────────────────────────────────────────┐
│  ┌────────┐  ┌──────────────────────────┐  ┌───────────────────┐  │
│  │        │  │                          │  │                   │  │
│  │  Side  │  │      Chat Window         │  │  Artifact Viewer  │  │
│  │  bar   │  │                          │  │  (conditional)    │  │
│  │        │  │                          │  │                   │  │
│  │ 280px  │  │      Flex 1 (grow)       │  │  420px            │  │
│  │        │  │                          │  │                   │  │
│  │        │  │                          │  │                   │  │
│  │        │  ├──────────────────────────┤  │                   │  │
│  │        │  │  Input Bar               │  │                   │  │
│  └────────┘  └──────────────────────────┘  └───────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Layout Specifications

| Zone | Width | Behavior |
| ---- | ----- | -------- |
| **Sidebar** | 280px fixed | Collapsible on mobile (hamburger menu). Contains: session list, new chat button, settings toggle, provider badge |
| **Chat Window** | Flex grow (fills remaining) | Min-width 400px. Scrollable message list + fixed input bar at bottom |
| **Artifact Viewer** | 420px fixed | Slides in from right when artifact is generated. Overlay on mobile |

### 4.3 Navigation Hierarchy

```
App Root
├── Sidebar
│   ├── Logo / App Name
│   ├── New Chat Button (primary CTA)
│   ├── Session List (sorted by recency)
│   │   └── Session Item (title, timestamp, message count)
│   ├── Settings Toggle
│   │   ├── LLM Provider Selector
│   │   ├── Model Selector
│   │   ├── Theme Toggle
│   │   └── Provider Status Indicators
│   └── Provider Badge (bottom of sidebar)
│
├── Chat Window
│   ├── Chat Header (session title, model badge)
│   ├── Message List
│   │   ├── Welcome Screen (empty state)
│   │   ├── User Message Bubble
│   │   ├── Assistant Message Bubble
│   │   │   ├── Markdown Rendered Content
│   │   │   ├── Source Citations (collapsible)
│   │   │   └── Action Buttons (copy, create artifact)
│   │   └── Streaming Indicator
│   └── Input Bar
│       ├── Text Input (auto-resize)
│       ├── Send Button
│       └── Keyboard Hint (Shift+Enter for newline)
│
└── Artifact Viewer (conditional)
    ├── Viewer Header (title, close button)
    ├── Toolbar (copy, download, raw/rendered toggle)
    ├── Render Area
    │   ├── Markdown Renderer
    │   └── HTML Sandbox (iframe)
    └── Resize Handle
```

---

## 5. Key Interaction States

### 5.1 Chat Message States

| State | Visual Treatment |
| ----- | --------------- |
| **User sending** | Message appears with subtle opacity animation; send button becomes spinner |
| **Streaming response** | Typing indicator (3 pulsing dots) → text appears character by character with cursor blink |
| **Response complete** | Full message with source citations revealed; action buttons fade in |
| **Error response** | Red-tinted message bubble with error icon; "Retry" button |
| **No sources found** | Amber-tinted callout: "I couldn't find relevant transcript sources for this question" |

### 5.2 Session Management States

| State | Visual Treatment |
| ----- | --------------- |
| **Active session** | Highlighted in sidebar with accent color left border |
| **Session hover** | Subtle background change; delete button appears |
| **Creating session** | Brief skeleton loading animation |
| **Empty session list** | Illustration + "Start your first chat" prompt |

### 5.3 Provider Status States

| State | Badge | Indicator |
| ----- | ----- | --------- |
| **Connected (Local)** | `🟢 Ollama · llama3.2` | Green dot |
| **Connected (Cloud)** | `🟢 Claude · Sonnet` | Green dot |
| **Switching** | `🟡 Switching...` | Amber spinner |
| **Disconnected** | `🔴 Ollama Unavailable` | Red dot + fallback notice |
| **No provider** | `⚫ No LLM Configured` | Gray dot + setup prompt |

### 5.4 Artifact Viewer States

| State | Visual Treatment |
| ----- | --------------- |
| **Generating** | Skeleton loader in viewer panel |
| **Rendered (Markdown)** | Formatted markdown with syntax highlighting |
| **Rendered (HTML)** | Sandboxed iframe with rendered content |
| **Raw view** | Monospace code view with copy button |
| **Error** | Error message with "Regenerate" button |

---

## 6. Component Design

### 6.1 Message Bubble

```
┌─────────────────────────────────────────────┐
│ 🤖 Assistant                    2:30 PM      │
├─────────────────────────────────────────────┤
│                                             │
│ Based on Lenny's conversation with          │
│ **Rahul Vohra** (Episode #45), product-     │
│ market fit can be measured using the...     │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 📎 Source: Episode #45 - Rahul Vohra    │ │
│ │ "The question is: how would you feel    │ │
│ │ if you could no longer use the product?"│ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 📎 Source: Episode #78 - Shishir Mehro..│ │
│ │ "PMF isn't binary. It's a spectrum..."  │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│              [📋 Copy] [📄 Artifact]        │
└─────────────────────────────────────────────┘
```

### 6.2 Source Citation Card

```css
.citation-card {
  background: var(--citation-bg);
  border-left: 3px solid var(--citation-border);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 8px 0;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background 0.2s ease;
}

.citation-card:hover {
  background: color-mix(in srgb, var(--citation-bg) 80%, var(--citation-border));
}

.citation-source {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.citation-excerpt {
  color: var(--text-secondary);
  font-style: italic;
  margin-top: 4px;
  line-height: var(--leading-relaxed);
}
```

### 6.3 Input Bar

```
┌─────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────┐ ┌─┐│
│ │ Ask about product management, growth, or...     │ │▶││
│ │                                                 │ │ ││
│ └─────────────────────────────────────────────────┘ └─┘│
│  Shift+Enter for new line                    Ollama 🟢 │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Responsive Behavior

### 7.1 Breakpoints

| Breakpoint | Width | Layout Change |
| ---------- | ----- | ------------- |
| **Desktop** | ≥ 1280px | Full three-column layout |
| **Laptop** | 1024–1279px | Sidebar + Chat + Artifact (artifact slightly narrower) |
| **Tablet** | 768–1023px | Sidebar collapses to hamburger; Artifact opens as overlay |
| **Mobile** | < 768px | Full-screen chat; sidebar as drawer; artifact as modal |

### 7.2 Mobile Adaptations

- **Sidebar**: Transforms into a slide-out drawer (left edge swipe or hamburger button)
- **Chat**: Full width. Input bar sticks to bottom above keyboard.
- **Artifact Viewer**: Full-screen modal with swipe-to-dismiss
- **Settings**: Bottom sheet modal
- **Provider Badge**: Moves to chat header bar

---

## 8. Accessibility Considerations

### 8.1 WCAG 2.1 AA Compliance

| Requirement | Implementation |
| ----------- | -------------- |
| **Color Contrast** | All text meets 4.5:1 (normal) / 3:1 (large) contrast ratios |
| **Keyboard Navigation** | Full tab order: sidebar → session items → input → send → messages → artifact |
| **Screen Reader** | ARIA labels on all interactive elements; `role="region"` on major zones |
| **Focus Indicators** | Visible focus ring (2px accent outline) on all focusable elements |
| **Reduced Motion** | `@media (prefers-reduced-motion: reduce)` disables animations |
| **Text Scaling** | All typography uses `rem` units; layout adjusts to 200% zoom |

### 8.2 ARIA Landmarks

```html
<aside role="complementary" aria-label="Chat sessions">
  <!-- Sidebar -->
</aside>

<main role="main" aria-label="Chat conversation">
  <!-- Chat Window -->
  <div role="log" aria-live="polite" aria-label="Message history">
    <!-- Messages -->
  </div>
</main>

<aside role="complementary" aria-label="Artifact viewer">
  <!-- Artifact Viewer -->
</aside>
```

### 8.3 Keyboard Shortcuts

| Shortcut | Action |
| -------- | ------ |
| `Ctrl/Cmd + N` | New chat session |
| `Ctrl/Cmd + K` | Focus search/input |
| `Escape` | Close artifact viewer / settings panel |
| `Enter` | Send message |
| `Shift + Enter` | New line in input |
| `Ctrl/Cmd + Shift + C` | Copy last assistant response |

---

## 9. Animation & Micro-Interactions

### 9.1 Animation Guidelines

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 9.2 Key Animations

| Element | Animation | Duration |
| ------- | --------- | -------- |
| Message appear | Fade up + slide (translateY: 8px → 0) | 250ms |
| Streaming text | Character-by-character with cursor blink | Real-time |
| Typing indicator | 3 dots with staggered pulse (0.6s loop) | Continuous |
| Sidebar session | Fade in with stagger delay | 150ms each |
| Artifact panel slide | translateX(100%) → 0 with ease-out | 300ms |
| Button hover | Background color shift + slight scale(1.02) | 150ms |
| Citation expand | Height auto-animate with clip-path | 200ms |
| Toast notification | Slide down + fade, auto-dismiss | 300ms in, 3s visible |
| Provider switch | Badge color cross-fade | 200ms |
| Error shake | translateX oscillation (0 → 4px → -4px → 0) | 300ms |

---

## 10. Design Decisions Log

| Decision | Chosen | Alternatives Considered | Rationale |
| -------- | ------ | ---------------------- | --------- |
| Three-panel layout | ✅ Sidebar + Chat + Artifact | Tab-based, modal-based | Keeps all context visible; mirrors Claude Artifacts UX |
| Source citations inline | ✅ Below each message | Separate panel, hover tooltips | Reinforces groundedness; always visible without extra action |
| SSE streaming | ✅ Character-by-character | Chunk-by-chunk, complete response | Most natural chat feel; reduces perceived latency |
| Provider badge always visible | ✅ Sidebar bottom + chat header | Only in settings | Users should always know which model is responding |
| iframe sandbox for HTML | ✅ `sandbox="allow-same-origin"` | Shadow DOM, CSP-only | Strongest isolation; prevents all script execution |
| Zustand for state | ✅ Zustand | Redux, Context API, Jotai | Lightweight, minimal boilerplate, excellent TypeScript support |
| Inter font | ✅ Inter | Roboto, Outfit, System fonts | Best readability at all sizes; widely recognized as premium |
| Warm indigo accent | ✅ #6366F1 | Blue (#3B82F6), Purple (#8B5CF6) | Professional yet warm; distinct from generic blue SaaS |
