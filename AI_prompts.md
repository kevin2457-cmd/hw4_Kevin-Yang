# AI Prompts

Running log of the prompts I gave my AI coding assistant for Homework 4 (Campus Customs).

---

## Problem 1 — AI Prompts Log

**Prompt:**

```text
Create a file named `AI_prompts.md` in the root of this homework project.
Set it up as a clean running log for Problems 1 through 10.
For each problem, create a section with:

* problem number and title
* the prompt I used
* an optional follow-up prompt
* a short note explaining what was missing from the first attempt, if a follow-up was needed

For now, only create the structure of the file. Do not work on any later homework problems and do not invent prompts that I have not actually used yet.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 2 — Analyze the Database

**Prompt:**

```text
Work only on Problem 2.

Inspect the existing `campus_customs.db` SQLite database in this project and understand its structure and contents.

Please:

1. Identify all tables in the database.
2. For each table, list:
   - table name
   - column names
   - data types
   - primary keys and foreign keys, if any
3. Briefly inspect representative rows from each table so you understand what the data represents.
4. Pay particular attention to the tables related to:
   - product catalogue
   - inventory
   - users
5. Explain how the tables relate to each other and which fields will likely be useful later for:
   - displaying products
   - checking price and inventory
   - user accounts
   - the AI shopping assistant
6. Create or update `output/harness.md` with a clear summary of the database structure and your findings.

Do not modify the database.
Do not build the website yet.
Do not implement login, FastAPI, or the AI agent yet.
Do not work on any later problems.

Only complete the database inspection and documentation required for Problem 2.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 3 — Build the Campus Customs Website

**Prompt:**

```text
Work only on Problem 3.

Build the initial Campus Customs storefront frontend using React, Vite, and TypeScript.

Use the existing project structure and the existing `campus_customs.db` data as the source of truth for product information.

Create a clean, functional Campus Customs ecommerce website with the following pages and features:

1. Home page
   - Campus Customs branding
   - simple hero section
   - navigation to Products, About, Login, and Create Account
   - feature or preview several products

2. Products page
   - display the products from the existing catalogue data
   - each product card should show:
     - product image
     - product name
     - price
     - garment/category information where appropriate
   - clicking a product should open its product detail page

3. Product detail page
   - product image
   - product name
   - description
   - price
   - available colors
   - sizes
   - inventory availability by size where the existing data supports it

4. About page
   - create a simple Campus Customs store description appropriate for a Yale campus apparel shop

5. Login page
   - create the frontend form only
   - email and password fields
   - do not implement authentication yet

6. Create Account page
   - create the frontend form only
   - first name
   - last name
   - email
   - password
   - do not implement account creation yet

7. Chat interface
   - add a chat button or compact chat widget in the bottom-right corner of the website
   - users should be able to open and close it
   - create the frontend interface only
   - do not connect it to an AI agent yet

8. Navigation
   - make navigation consistent across the site
   - clearly show links for Home, Products, About, Login, and Create Account

Important constraints:

- Use React + Vite + TypeScript.
- Reuse the existing product images and product data.
- Do not invent product prices, inventory, colors, or descriptions when those values already exist in the database.
- Keep the code organized into reasonable reusable components.
- Make sure the site can run locally using the normal project development command.
- Do not implement login or account creation functionality yet.
- Do not build FastAPI.
- Do not implement PydanticAI.
- Do not connect the chatbot to an AI model.
- Do not work on Problems 4 or later.

Only complete the initial storefront frontend required for Problem 3.
```

**Follow-up prompt (optional):**

```text
(Answer to the assistant's clarifying question) Build the small FastAPI app as the assignment requires — backend/main.py should only serve products and images, no login or AI.
```

**What the first prompt was missing:**

My first prompt said "Do not build FastAPI," but the browser can't read SQLite directly and Problem 3 actually requires a simple `backend/main.py` to serve products and images, so I had to allow a minimal read-only FastAPI backend.

---

## Problem 4 — Create Account and Log In

**Prompt:**

```text
Work only on Problem 4.

Implement user registration and login for the existing Campus Customs application.

Use the existing `users` table in `data/campus_customs.db` as the source of truth.

Requirements:

1. User registration
   - Connect the existing Create Account form to the backend.
   - Accept:
     - first name
     - last name
     - email
     - password
   - Create a new row in the existing `users` table.
   - Populate the required `name` field using the user's first and last name.
   - Do not store passwords in plaintext.
   - Hash passwords securely before saving them.
   - Prevent duplicate accounts using the same email.
   - Return a clear success or error response to the frontend.

2. User login
   - Connect the existing Login form to the backend.
   - Accept email and password.
   - Look up the user by email.
   - Verify the entered password against the stored password hash.
   - Existing users already in the database must still be able to log in.
   - In particular, preserve compatibility with the existing password hash format:
     `pbkdf2_sha256$<salt>$<hex digest>`

3. Authentication state
   - After successful login, the frontend should know which user is logged in.
   - Display the logged-in user's name somewhere appropriate in the UI.
   - Provide a logout action.
   - Keep the implementation simple and appropriate for this homework.

4. Backend
   - Extend the existing FastAPI backend instead of replacing it.
   - Add only the authentication/account endpoints needed for this problem.
   - Do not break the existing product APIs from Problem 3.

5. Frontend
   - Keep the existing site design and pages.
   - Show useful validation/error messages for cases such as:
     - incorrect password
     - account not found
     - duplicate email
     - missing required fields

Important constraints:

- Use the existing SQLite database.
- Do not recreate or replace the database.
- Do not delete existing users.
- Never store plaintext passwords.
- Make sure the existing test account remains compatible.
- Do not implement the AI shopping agent yet.
- Do not implement PydanticAI yet.
- Do not implement chat memory yet.
- Do not work on Problem 5 or later.

Test both registration and login locally and confirm that:
- a new user can create an account,
- the new database row is created correctly,
- the password is hashed,
- the new user can log in,
- an existing user can still log in,
- logout works.

Only complete Problem 4.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 5 — PydanticAI Agent Backend

**Prompt:**

```text
Work only on Problem 5.

Extend the existing Campus Customs FastAPI backend by adding a PydanticAI-based shopping assistant.

Keep the existing storefront, product API, login, and registration functionality working.

Build the AI agent backend with a clean structure.

Required files / organization:

1. `backend/main.py`
   - Keep the existing FastAPI application.
   - Add the API endpoint needed for the chat interface to send a user message and receive an assistant response.
   - Do not remove or break the existing product or authentication endpoints.

2. `backend/agent.py`
   - Define the PydanticAI agent.
   - Use the model configuration already expected by this project.
   - Load the agent instructions from an external prompt file rather than hard-coding a long system prompt directly in Python.

3. `backend/tools.py`
   - Create a place for agent tools.
   - Only implement tools required for Problem 5.
   - Keep database access and tool logic separated from the main agent definition where practical.

4. `backend/models.py`
   - Define any Pydantic request/response models needed for the chat API and agent interaction.

5. `prompts/prompt.md`
   - Create the system prompt for the Campus Customs shopping assistant.
   - The assistant should act like a helpful Campus Customs store associate.
   - It should be concise, friendly, and focused on helping users shop.
   - It must not invent product facts, prices, colors, or inventory.
   - If information is unavailable, it should say so rather than guessing.

Chat integration:

6. Connect the existing frontend chat widget to the new backend chat endpoint.

7. A user should be able to:
   - open the existing chat widget,
   - type a message,
   - send it to the FastAPI backend,
   - receive an AI-generated response,
   - see the response displayed in the chat interface.

8. Add basic UI states:
   - sending/loading state,
   - backend or model error message,
   - prevent accidental duplicate sends while a request is in progress.

Important constraints:

- Use PydanticAI for the agent.
- Extend the existing FastAPI backend rather than creating a separate unrelated app.
- Keep prompts in `prompts/prompt.md`.
- Keep code organized across `main.py`, `agent.py`, `tools.py`, and `models.py`.
- Reuse the existing project structure.
- Do not recreate the database.
- Do not break product browsing or authentication.
- Do not hard-code fake product information in the agent.
- Do not implement advanced product-card rendering yet.
- Do not implement persistent chat history yet unless Problem 5 explicitly requires it.
- Do not work on Problem 6 or later.

Test the full path locally:
React chat widget -> FastAPI chat endpoint -> PydanticAI agent -> response displayed in the browser.

Only complete Problem 5.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 6 — Product and Inventory Tools

**Prompt:**

```text
Work only on Problem 6.

Extend the existing Campus Customs PydanticAI shopping assistant so it can retrieve accurate product information directly from the existing SQLite database.

Use `data/campus_customs.db` as the source of truth.

Main goal:
The AI shopping assistant must use tools to look up real Campus Customs product information instead of inventing product details.

Implement the required database-backed tools in `backend/tools.py`.

Required functionality:

1. Product search tool
   - Allow the agent to search Campus Customs products using natural-language keywords.
   - Search relevant catalogue fields such as:
     - product name
     - garment type
     - search tags
     - colors
     - description
   - Handle inconsistent garment type wording reasonably.
   - For example, a user asking for "hoodies" should still be able to find products whose garment_type may say:
     - hoodie
     - pullover hoodie
     - hooded sweatshirt

2. Product detail lookup
   - Allow the agent to retrieve accurate details for a specific product using its product ID.
   - Return useful fields such as:
     - product_id
     - name
     - garment_type
     - description
     - colors
     - price
     - image information where useful

3. Inventory lookup
   - Allow the agent to retrieve real inventory for a product.
   - Return stock by size:
     - XS
     - S
     - M
     - L
     - XL
     - XXL
   - Report the actual quantity stored in the `inventory` table.
   - Treat quantity 0 as out of stock.

4. Database grounding
   - Product prices must come from `catalogue.price`.
   - Colors must come from `catalogue.colors`.
   - Descriptions must come from the catalogue.
   - Inventory must come from the `inventory` table.
   - Do not hard-code product facts into the agent prompt.

5. JSON fields
   - Remember that `colors` and `search_tags` are JSON arrays stored as TEXT in SQLite.
   - Parse them correctly before returning data to the agent.

6. Agent integration
   - Register the new tools with the existing PydanticAI agent.
   - Update the agent instructions only as needed so that it knows to use database tools for factual product questions.

7. Behavior
   The assistant should correctly handle questions such as:
   - "What hoodies do you have?"
   - "How much is the Basic Hoodie Big Yale?"
   - "What colors does this hoodie come in?"
   - "Do you have this product in medium?"
   - "How many XL are left?"
   - "Do you have any Yale t-shirts?"

8. Accuracy rules
   - Never invent a product.
   - Never invent a price.
   - Never invent a color.
   - Never invent inventory.
   - If a product cannot be found, say so.
   - If a requested color or size is unavailable, clearly say it is unavailable.
   - If inventory is 0, clearly indicate that size is out of stock.

9. Preserve existing functionality
   - Keep the storefront working.
   - Keep login and registration working.
   - Keep the existing chat endpoint working.
   - Do not recreate or modify the database schema unless absolutely required by Problem 6.

Testing:

Test the agent locally with several realistic shopping questions and verify its answers directly against `campus_customs.db`.

At minimum test:
- a broad category search,
- a specific product price question,
- a color question,
- an in-stock size question,
- an out-of-stock size question,
- a product that does not exist.

Important constraints:

- Work only on Problem 6.
- Do not implement dynamic product-card rendering yet.
- Do not implement persistent chat history yet.
- Do not implement later Problem 7 or Problem 8 functionality.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 7 — Dynamic Product Cards from Chat

**Prompt:**

```text
Work only on Problem 7.

Extend the existing Campus Customs AI shopping assistant so that product recommendations returned by the agent can be displayed dynamically as product cards inside the chat interface.

Build on the existing functionality from Problems 3–6.

Main goal:
When the user asks the chatbot about products, the agent should be able to return structured product information in addition to its normal text response, and the React frontend should render those products visually.

Requirements:

1. Structured chat response

Update the backend chat response so it can return both:

- the assistant's text response
- a structured list of relevant products

Each returned product should use real information from the existing database and include useful fields such as:

- product_id
- name
- garment_type
- price
- image_url
- colors
- inventory information where appropriate

Use appropriate Pydantic models in `backend/models.py` for the structured response.

2. Agent integration

Use the existing PydanticAI agent and database-backed product tools from Problem 6.

When a user's request identifies or recommends relevant products, make those real database products available to the frontend as structured data.

Do not attempt to extract product names from the AI's plain-text response on the frontend.

The structured product information should come from the backend.

3. Product cards in chat

Update the existing React chat interface so that products returned by the backend appear as product cards associated with the assistant's response.

Each product card should display at least:

- product image
- product name
- price

Include other useful information such as available colors or garment type if appropriate.

4. Product navigation

Make each chat product card clickable.

Clicking a product card should take the user to the existing product detail page for that product using its real `product_id`.

Do not create a separate duplicate product page.

5. Multiple products

Support responses containing multiple products.

For example, if the user asks:

"What hoodies do you have?"

the assistant should be able to return several relevant hoodie products and the chat interface should render multiple product cards.

6. No-result behavior

If no matching product exists:

- do not create fake product cards
- return an empty product list
- let the assistant explain that no matching item was found

7. Data accuracy

All displayed product data must come from `data/campus_customs.db`.

Do not invent:

- product names
- images
- prices
- colors
- inventory

Reuse the existing product/database utilities where possible instead of duplicating database logic.

8. Preserve normal conversation

Not every assistant response needs product cards.

For example:

"Hello"
"How can you help me?"
"Thanks"

should still work as normal text chat messages without unnecessary product cards.

9. Preserve existing functionality

Do not break:

- product browsing
- product detail pages
- login
- registration
- logout
- existing FastAPI product endpoints
- the PydanticAI agent
- database-backed tools from Problem 6

Testing:

Test at least these cases:

1. "What hoodies do you have?"
   -> text response plus multiple real hoodie product cards

2. Ask for a specific existing product
   -> relevant product card appears

3. Ask for a nonexistent product
   -> no fake card is displayed

4. Click a product card
   -> opens the correct existing product detail page

5. Ask a normal non-product conversational question
   -> text response works without unnecessary cards

Important constraints:

- Work only on Problem 7.
- Do not implement persistent chat history yet.
- Do not implement later user-memory functionality.
- Do not work on Problem 8 or later.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 8 — Chat Memory and User Context

**Prompt:**

```text
Work only on Problem 8.

Extend the existing Campus Customs AI shopping assistant so that it has persistent chat history for logged-in users and can understand relevant user and page context.

Build on the existing implementation from Problems 3–7.

Main goals:

1. Save chat history for logged-in users.
2. Restore prior chat history when the user returns.
3. Give the agent access to the logged-in user's identity.
4. Give the agent context about the product page the user is currently viewing.
5. Allow follow-up questions such as "Do you have this in pink?" to work correctly when the current product is known.

Use the existing SQLite database and the existing `chat_messages` table.

Requirements:

1. Persistent chat history

For logged-in users, save each chat message to the existing `chat_messages` table.

Store:

- user_id
- role (`user` or `assistant`)
- content
- products_json when an assistant response includes product cards
- created_at using the existing database behavior

Do not create a separate chat-history database.

2. Load previous messages

When a logged-in user opens the chat interface:

- retrieve that user's previous chat messages
- return them in chronological order
- display them in the chat widget

Make sure one user's chat history is never shown to another user.

3. Product cards in history

If an older assistant message has `products_json`:

- parse the saved JSON
- restore the associated product cards in the frontend

Previously recommended products should still display correctly after refreshing or reopening the app.

4. Logged-in user context

Provide the agent with useful context about the current logged-in user.

At minimum, make the user's identity available to the agent, such as:

- user_id
- first_name
- last_name
- email where appropriate

Use the user's first name naturally when useful, but do not over-personalize every response.

5. Current product context

When the user is viewing a product detail page, send the current product's `product_id` to the chat backend as context.

The backend should retrieve the real product information from the database when needed.

This should allow the assistant to understand references such as:

- "Do you have this in pink?"
- "Do you have this in medium?"
- "How much is this?"
- "Is this available in XL?"

Do not rely on the language model guessing what "this" means.

6. Agent context

Provide relevant conversation history and current context to the PydanticAI agent so it can answer follow-up questions consistently.

Use the existing agent structure rather than creating a second unrelated agent.

Do not put large amounts of unnecessary data into every request.

7. Anonymous users

If the current implementation allows users to chat without logging in:

- normal chat may still work
- do not save anonymous messages into another user's history
- do not falsely associate an anonymous conversation with a logged-in account

Keep this behavior simple.

8. API structure

Extend the existing FastAPI backend with the endpoints or request fields needed for:

- loading chat history
- saving messages
- passing current product context

Reuse the existing authentication/session approach from Problem 4.

Do not break the existing chat endpoint.

9. Security and data separation

A user must only be able to retrieve their own chat history.

Do not accept an arbitrary user_id from the frontend as trusted identity if the existing authentication state already identifies the logged-in user.

Use the existing authentication/session implementation to determine the active user where possible.

10. Preserve existing features

Do not break:

- storefront pages
- product browsing
- product detail pages
- registration
- login/logout
- product search tools
- inventory lookup
- chat product cards

Testing:

Test at least the following:

1. Log in as a user and send several chat messages.
   -> Messages are saved to `chat_messages`.

2. Refresh or reopen the app.
   -> Previous messages reappear in the correct order.

3. Assistant responses containing product cards.
   -> Cards reappear correctly from `products_json`.

4. Log in as a different user.
   -> The first user's messages are not visible.

5. Open a specific product detail page and ask:
   "Do you have this in pink?"
   -> The agent understands which current product "this" refers to and checks the real database data.

6. Ask:
   "Do you have this in medium?"
   -> The agent checks the real inventory for the current product.

7. Ask a follow-up question based on an earlier chat message.
   -> The agent uses conversation history appropriately.

Important constraints:

- Work only on Problem 8.
- Use the existing `chat_messages` table.
- Do not recreate the database.
- Do not invent product facts.
- Do not implement Problem 9 usability improvements yet.
- Do not redesign the site for Problem 10 yet.

Only complete the context and persistent-memory functionality required for Problem 8.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 9 — Usability Improvements

**Prompt:**

```text
Work only on Problem 9.

Review the existing Campus Customs application from Problems 3–8 and implement four meaningful usability improvements:

- 2 frontend usability improvements
- 2 AI agent / backend usability improvements

The improvements must be real, implemented changes, not just suggestions.

Do not redesign the entire site yet. Problem 10 will handle broader visual/design improvements.

Choose improvements that make the existing shopping experience easier, clearer, or more useful.

FRONTEND USABILITY IMPROVEMENTS

Implement two meaningful frontend improvements.

Good examples include:

1. Product search and filtering
   - Add an easy way for users to search or filter the product catalogue.
   - Allow useful filtering such as product type, price, or availability.
   - Make sure filtering uses the real product data already loaded from the backend.

2. Better inventory / size feedback
   - Clearly distinguish available and sold-out sizes on product detail pages.
   - Disable or visually identify sizes with quantity 0.
   - Show useful availability information without requiring the user to ask the chatbot.

Other reasonable frontend improvements are acceptable if they provide clear usability value.

Do not add cosmetic changes only. The improvements should help the user complete a shopping task more easily.

AGENT / BACKEND USABILITY IMPROVEMENTS

Implement two meaningful improvements to the AI shopping assistant or backend.

Good examples include:

1. Better handling of ambiguous requests
   - If a user gives an unclear shopping request, the assistant should ask a useful clarifying question rather than guessing.
   - Example:
     "I want a Yale shirt"
     -> ask about preferences such as style, color, size, or budget when that would materially improve the recommendation.

2. Better product comparison / recommendation behavior
   - Allow the assistant to compare multiple real Campus Customs products using database-backed facts.
   - It may compare fields such as:
     - price
     - garment type
     - colors
     - inventory
   - Do not invent subjective product facts that are not supported by the database.

Other meaningful agent/backend improvements are acceptable if they improve reliability, usefulness, or shopping usability.

GENERAL REQUIREMENTS

- Preserve all existing functionality from Problems 3–8.
- Continue using `data/campus_customs.db` as the source of truth.
- Do not invent product data.
- Do not remove product browsing, authentication, chat history, current-product context, or product-card functionality.
- Keep the implementation clean and consistent with the existing codebase.
- Do not work on the full visual redesign required for Problem 10.

DOCUMENTATION

Create or update:

`output/usability.md`

Document exactly four implemented improvements.

Use this structure:

# Usability Improvements

## Frontend Improvement 1
- Problem:
- Change implemented:
- Why it improves usability:
- Files changed:

## Frontend Improvement 2
- Problem:
- Change implemented:
- Why it improves usability:
- Files changed:

## Agent / Backend Improvement 1
- Problem:
- Change implemented:
- Why it improves usability:
- Files changed:

## Agent / Backend Improvement 2
- Problem:
- Change implemented:
- Why it improves usability:
- Files changed:

Only document improvements that were actually implemented and tested.

TESTING

Test all four improvements locally.

Also verify that the following still work:

- Home page
- Products page
- Product detail pages
- Login and registration
- Logout
- AI chat
- database-backed product search
- inventory questions
- product cards in chat
- persistent chat history
- current-product context

Only complete Problem 9.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 10 — Site Design

**Prompt:**

```text
Work only on Problem 10.

Improve the visual design and overall polish of the existing Campus Customs application.

Do not rebuild the project from scratch.
Do not remove or break functionality from Problems 3–9.

Main goal:
Make the website look like a cohesive, professional Campus Customs / Yale campus apparel ecommerce site rather than a default Vite student project.

DESIGN REQUIREMENTS

1. Create a consistent visual system

Use a cohesive visual language across the entire site, including:

- typography
- spacing
- buttons
- cards
- navigation
- forms
- page containers
- headings
- colors
- hover/focus states

Use a clean collegiate / campus apparel aesthetic.

2. Improve the header and navigation

Refine the existing navigation so it feels like a real ecommerce site.

Keep the existing navigation functionality, including:

- Home
- Products
- About
- Login / account state
- Create Account where appropriate
- Logout for logged-in users

Do not remove any working navigation behavior.

3. Improve the Home page

Make the home page more visually intentional.

Improve areas such as:

- hero section
- headline hierarchy
- call-to-action buttons
- featured product presentation
- spacing and layout

Use real existing Campus Customs products when displaying featured merchandise.

Do not invent product data.

4. Improve the Products page

Make the product catalogue look more polished and easy to browse.

Improve:

- product card layout
- image sizing
- product name hierarchy
- price presentation
- spacing
- responsive grid behavior

Preserve the search/filter usability improvements from Problem 9.

5. Improve the Product Detail page

Create a cleaner ecommerce product-detail layout.

Improve presentation of:

- product image
- product name
- price
- description
- colors
- size availability
- inventory feedback

Preserve real database information and sold-out size behavior.

6. Improve authentication pages

Polish:

- Login
- Create Account

Use consistent:

- form widths
- labels
- input styling
- validation messages
- buttons
- spacing

Do not change the working authentication logic unless necessary for presentation.

7. Improve the chat interface

Polish the existing AI shopping assistant UI.

Improve:

- chat launcher
- open chat panel
- message bubbles
- user vs assistant message distinction
- product recommendation cards
- loading state
- input field
- send button
- scrolling behavior

Keep persistent history and product-page context working.

Do not remove any AI functionality.

8. Responsive design

Make the application usable on different browser sizes.

At minimum:

- avoid horizontal overflow
- make product grids responsive
- keep navigation usable
- make forms readable
- ensure the chat widget fits smaller screens
- ensure product detail pages reflow appropriately

9. Accessibility and interaction polish

Where practical, improve:

- readable contrast
- visible focus states
- button/link hover states
- meaningful labels
- clickable areas
- disabled-state clarity

Do not prioritize cosmetic animation over usability.

10. Keep the design appropriate

Avoid:

- excessive animation
- overly complex effects
- unrelated gradients
- generic AI dashboard styling
- fake luxury branding
- visual elements that do not fit a campus apparel store

The final design should feel simple, modern, collegiate, and ecommerce-focused.

DOCUMENTATION

Create:

`output/design.md`

Document the final design decisions.

Use a structure such as:

# Design

## Overall Direction
Briefly explain the intended visual style and why it fits Campus Customs.

## Visual System
Describe:
- typography
- color approach
- spacing
- buttons
- cards

## Page Improvements
Describe major visual changes made to:
- Home
- Products
- Product Detail
- Login / Create Account
- Chat

## Responsive Design
Explain how the design adapts to smaller screens.

## Files Changed
List the main frontend files or stylesheets modified.

Only describe design changes that were actually implemented.

FINAL VERIFICATION

Before finishing, run and inspect the application locally.

Verify that all earlier functionality still works:

- product catalogue
- product detail pages
- product search/filtering
- real prices and inventory
- registration
- login/logout
- AI chatbot
- database-backed product lookup
- structured product cards in chat
- persistent chat history
- current-product context
- usability improvements from Problem 9

Do not replace working functionality merely for visual changes.

Only complete Problem 10.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 11 — Site Testing (App Check)

**Prompt:**

```text
帮我完成 HW4 Problem 11。

现在检查我前面已经做好的网站，实际测试三个功能，并整理成最后要提交的 app check。

请完成：

1. 测试 chatbot 查询一个真实商品的价格或者库存，确认回答和数据库一致。
2. 测试 dynamic product cards，比如问：
   “What hoodies do you have?”
   确认聊天里会显示真实商品卡片。
3. 测试我 Problem 9 里做的一个 usability improvement，比如 product search/filter，或者 sold-out size disabled。

每一项都要实际测试，并截一张能清楚证明功能正常的截图。

把截图放到：
`output/app_check_images/`

然后创建：
`output/app_check.html`

这个 HTML 里按顺序放三组测试：
- 测试内容
- 截图
- 简短说明这个功能测试了什么、结果是否正常

确保双击 `output/app_check.html` 可以直接打开并看到所有截图。

不要修改我已经做好的功能，除非测试过程中发现明显 bug。
如果发现 bug，先修复，再重新测试并截图。

只完成 Problem 11。
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 12 — Audit Trail, Safety, and Harness

**Prompt:**

```text
帮我完成 HW4 Problem 12。

在不破坏我前面已经完成的功能的前提下，把 audit trail、安全规则和 harness 文档补完整。

请完成下面这些内容：

1. Audit trail

创建或完善：

`output/audit_trail.json`

要求：

- 用来记录 agent 每次运行中的关键过程。
- 记录内容至少包括：
  - timestamp
  - 用户请求的简短描述
  - agent 调用了什么 tool
  - tool 的主要参数
  - tool 返回结果的简短摘要
  - agent 最后为什么停止
- audit trail 必须是 append-only。
- 不要每次运行都覆盖之前的记录。
- 不要在 audit trail 里记录密码、API key、完整认证 token 或其他敏感信息。
- 参数和结果只需要保留足够用于检查和调试的信息，不要把大量原始数据全部写进去。
- 如果一次请求调用了多个 tools，要能看出调用顺序。

把 audit trail 集成到现有 agent flow 中，但不要因为记录日志而改变 agent 原来的正常行为。

2. Safety rules

检查并更新：

`prompts/prompt.md`

在现有 shopping assistant prompt 的基础上加入明确的安全和可靠性规则。

至少包括：

- 不允许编造商品。
- 不允许编造价格。
- 不允许编造颜色。
- 不允许编造库存数量或尺码库存。
- 商品事实必须以数据库/tool 返回的数据为准。
- 如果查不到信息，要明确说不知道或者没有找到，而不是猜测。
- 如果 tool 返回错误，不要假装查询成功。
- 不要泄露密码、password hash、API key、token 或其他敏感信息。
- 不要向用户显示数据库内部不必要的信息。
- 对模糊请求可以先问澄清问题。
- 不要声称已经完成数据库操作，除非对应操作实际成功。

不要删除我现有 prompt 中已经工作的购物助手行为，只补充必要的 safety rules。

3. Complete `output/harness.md`

把我之前的：

`output/harness.md`

补充完整。

保留原来 Problem 2 已经写好的 database analysis，不要删除。

在后面新增清晰的 sections，至少说明：

### Models

总结 `backend/models.py` 中现在实际存在的主要 Pydantic models。

对每个重要 model 说明：

- model 名称
- 主要 fields
- 每个 field 是干什么的
- 为什么需要这个 model

不要写不存在的 model。

### Agent Tools / Capabilities

列出现在实际实现的 agent tools 和主要能力。

例如如果实际存在的话，可以包括：

- product search
- product detail lookup
- price lookup
- inventory lookup
- user context
- current product context
- product recommendation cards

对每一个说明：

- 输入是什么
- 输出是什么
- 为什么 agent 需要它

只写项目里实际已经实现的工具和能力。

### Safety Rules

总结 `prompts/prompt.md` 里实际存在的 safety rules。

说明这些规则主要防止什么问题，例如：

- hallucinated price
- hallucinated inventory
- exposure of sensitive data
- false claims when a tool fails

### Agent / System Specs

记录当前项目的实际 technical specs。

至少检查并写清楚：

- 使用的 AI model
- PydanticAI agent 在哪里定义
- system prompt 文件位置
- FastAPI 入口
- React/Vite frontend 入口
- database path
- chat endpoint
- product endpoints
- authentication相关 endpoint（如果实际存在）
- chat history endpoint（如果实际存在）
- tool/result limits（如果代码里存在）
- agent loop limits / retry limits（如果代码里存在）
- product search result cap（如果代码里存在）
- frontend 如何启动
- backend 如何启动

必须根据当前代码实际检查，不要猜。

如果代码里没有明确设置 loop limit、result cap 或 retry limit，就在 harness 里明确写：
“Not explicitly configured”
而不是自己发明一个数字。

4. Audit trail verification

实际运行至少几次测试，确认：

- audit_trail.json 会产生记录
- 新记录会追加，不会覆盖旧记录
- tool calls 能被记录
- 不会写入密码、API key 或 token
- agent 原有功能仍然正常

可以测试例如：

- “What hoodies do you have?”
- 查询一个真实商品的价格
- 查询一个尺码库存

5. Regression check

完成以后，快速确认我前面的功能没有被改坏：

- products still load
- product detail page still works
- login / registration still work
- chatbot still works
- database-backed product lookup still works
- product cards still work
- chat history still works
- current-product context still works
- usability improvements still work

不要重写整个项目。
不要重构没有必要改动的文件。
尽量做最小范围修改，只完成 Problem 12。

最后告诉我：

1. 修改了哪些文件
2. audit trail 是怎么实现的
3. safety rules 加了哪些
4. harness 新增了哪些内容
5. 测试结果是否全部通过

只完成 Problem 12。
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_

---

## Problem 13 — GitHub Repository Submission

**Prompt:**

```text
帮我完成 HW4 Problem 13。

现在把我前面已经完成的 HW4 项目整理成最终可以提交到 GitHub 的版本。

不要重写项目功能，也不要修改已经正常工作的代码，主要做提交前整理和检查。

请完成下面这些内容：

1. 检查项目目录结构

确保最终项目根目录叫：

`hw4`

并且至少包含这些内容：

hw4/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── frontend/
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/
│       └── prompt.md
└── output/
    ├── harness.md
    ├── design.md
    ├── usability.md
    ├── app_check.html
    ├── app_check_images/
    └── audit_trail.json

不要为了匹配结构而删除我现有正常工作的必要文件。

2. 检查 `.gitignore`

确保下面这些内容不会被提交到 GitHub：

- `.env`
- `data/campus_customs.db`
- `data/products/`
- 任何真实 API key 或 secret
- Python cache files
- frontend node_modules
- build artifacts
- editor/system temporary files

如果 `.gitignore` 不完整，请补充。

3. 检查 `.env.example`

确保项目里有：

`.env.example`

这个文件只能包含环境变量名称和 placeholder。

例如：

OPENAI_API_KEY=your_api_key_here

绝对不要把真实 API key、token 或 secret 写进去。

4. Secret scan

检查整个准备提交的项目，确认没有：

- real API keys
- passwords
- tokens
- `.env` 内容
- hard-coded credentials
- private secrets

如果发现真实 secret，不要把它提交。

不要删除正常的测试用户名或普通非敏感示例数据，除非它确实属于 credential。

5. Local data

确认下面这些只保留在本地，不进入 Git：

`data/campus_customs.db`
`data/products/`

不要删除本地文件，只确保 Git 不跟踪它们。

6. requirements.txt

检查 backend 实际使用的 Python dependencies，并确保 `requirements.txt` 足够让老师安装并运行项目。

不要加入项目根本没有使用的随机依赖。

7. README.md

完善 README，让老师 clone repo 后能够理解怎么运行项目。

至少说明：

- project overview
- required local data pack location
- where to place:
  `data/campus_customs.db`
  `data/products/`
- how to create `.env` from `.env.example`
- how to install backend dependencies
- how to run FastAPI backend
- how to install frontend dependencies
- how to run the Vite frontend
- expected backend port
- expected frontend port if applicable

Backend instructions should match the actual project.

If the backend is run from the `backend` directory, document the correct command.

Do not invent commands that do not match the current code.

8. Final project check

Verify these required files actually exist:

- AI_prompts.md
- requirements.txt
- .env.example
- .gitignore
- README.md
- backend/main.py
- backend/agent.py
- backend/models.py
- backend/tools.py
- backend/prompts/prompt.md
- output/harness.md
- output/design.md
- output/usability.md
- output/app_check.html
- output/app_check_images/
- output/audit_trail.json

If something required is missing, tell me clearly.

9. Git safety check

Before I push, show me the exact files that Git would include if possible.

Confirm specifically that these are NOT included:

- `.env`
- `campus_customs.db`
- product images
- API keys

Do not create a zip file.

10. Final instructions for me

At the end, give me the exact commands I should run to:

- initialize git if needed
- add files
- commit
- connect my GitHub repo
- push to GitHub

Do not assume my GitHub repo URL. Use a placeholder for that command if necessary.

Also tell me what URL I should submit on Canvas.

Only complete Problem 13 and final GitHub submission preparation.
```

**Follow-up prompt (optional):**

_None yet._

**What the first prompt was missing:**

_N/A_
