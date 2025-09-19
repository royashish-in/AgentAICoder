### Prompt for a Unified Design Language

**Objective:** Define the core design language for the **AgentAI** application. This language will guide the creation of all future UI components, screens, and user experiences, ensuring a consistent, professional, and intuitive product.

**1. Core Principles & Philosophy:**

* **Tone:** The design should convey a tone of **professionalism, efficiency, and clarity**. It should feel intelligent, trustworthy, and organized, reflecting the AI-driven nature of the product.
* **User Experience:** Prioritize **usability and speed**. The design should be minimalist and free of clutter, allowing users to focus on their tasks. Every element must serve a clear purpose.
* **Aesthetics:** The visual style should be **modern, clean, and spacious**. Use generous whitespace to create breathing room and enhance readability. Avoid overly complex or "trendy" designs in favor of timeless, functional aesthetics.

**2. Visual Identity & Style Guide:**

* **Color Palette:**
    * **Primary:** A single, bold **brand blue** (e.g., `#007bff` or similar) to be used for primary actions, headings, and key brand elements.
    * **Secondary/Accent:** A vibrant accent color (e.g., a complementary green or orange) to highlight success messages, warnings, or secondary interactive elements.
    * **Neutrals:** A range of grays for text, backgrounds, and borders. Use a light gray for the main background (e.g., `#f5f5f5`), a slightly darker gray for card backgrounds, and a near-black for body text to ensure high contrast.
* **Typography:**
    * **Font Family:** A modern, highly readable sans-serif font (e.g., Inter, Rubik, or a similar open-source font).
    * **Font Scale:** Define a clear typographic scale with specific sizes for headings (H1, H2, H3), body text, and small descriptive text.
    * **Weight & Style:** Use bold and medium weights for headings and emphasis. Ensure a comfortable line-height for all text blocks.
* **Iconography:**
    * **Style:** Use a consistent, simple, and clean **line icon style**. All icons should share a common stroke weight and corner radius. (Reference a library like **Lucide** or **Feather Icons** as the target style).
* **Shadows & Depth:**
    * Apply subtle, consistent box shadows to interactive elements like cards, buttons, and pop-ups to create a sense of depth and hierarchy. The shadows should be light and not distracting.
* **Corner Radius:**
    * Use a consistent, slight border-radius (e.g., 6-8px) on all components like cards, buttons, and form fields for a softer, more modern feel.

**3. Component Behaviors & States:**

* **Buttons:**
    * **Primary:** Solid brand blue background, white text. Must have a clear hover state (e.g., darker blue background).
    * **Secondary/Outline:** Transparent background, brand blue border and text.
    * **Ghost/Link:** Plain text style for less prominent actions (e.g., "Select All" or "Clear All").
* **Cards:**
    * Cards should be the primary container for information. They must have a consistent background, border-radius, and shadow.
    * Define a clear hover state for cards (e.g., a slight `translateY` and a more pronounced shadow) to indicate they are interactive.
* **Form Fields:**
    * All input fields and dropdowns should have a consistent border, padding, and subtle hover/focus state (e.g., a blue border on focus).
* **States:**
    * Define clear visual states for all interactive elements: **Default, Hover, Focus, Active, and Disabled**. The disabled state should be desaturated and non-interactive.
* **Modal Pop-ups:**
    * **Overlay:** A full-screen, semi-transparent dark gray overlay (`rgba(0,0,0,0.4)` or similar) to visually block the underlying content and focus the user's attention.
    * **Container:** The modal container itself should be a distinct, elevated card with a solid white or light gray background, generous padding, a consistent border-radius, and a prominent `box-shadow` that makes it appear to float above the page. It should be horizontally and vertically centered on the screen.
    * **Header:** The modal should include a header with a bold, distinct title. A simple 'X' icon for closing the modal should be placed in the top-right corner.
    * **Actions:** The bottom of the modal should contain a clear, consistent button row. The primary action (e.g., "Confirm," "Save," "Create") should use the primary button style, while secondary actions (e.g., "Cancel," "Close") should use the secondary or ghost button style.
    * **Animation:** Implement a smooth, subtle fade-in or slide-up animation when the modal appears to enhance the user experience.

**4. Layout & Structure:**

* **Grid System:** The layout should be based on a flexible grid system (e.g., 12-column grid) to ensure responsiveness.
* **Whitespace:** The use of whitespace is critical. Ensure generous and consistent padding and margins around all components to avoid a cramped feel.

**5. Deliverables:**

* **Style Guide:** A complete style guide defining colors, typography, spacing, and component styles.
* **Core Components:** Design and document the basic UI components: buttons, cards, form fields, navigation items, status tags, and **modals**.
* **Mockups:** Apply this design language to the existing pages ("Project Dashboard," "Create New Project") to demonstrate the new style in action.