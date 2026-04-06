# 📖 How to Get Access to This Repository

This workflow automatically adds you to the **Readers** team when you raise a Pull Request.  
The repository is **public** — you can view and **fork** it freely.  
You **cannot push, modify, or delete** anything in this repo.

---

## 🚀 Step-by-Step Instructions for Users

### Step 1 — Fork the Repository
Click the **Fork** button at the top-right of this repository page to create your own copy.

![Fork button is at the top right of the repo page]

---

### Step 2 — Open `readers.txt`
In **your forked repository**, navigate to the file:

```
readers.txt
```

Click the ✏️ **pencil (Edit) icon** to edit the file directly in the browser.

---

### Step 3 — Add Your GitHub Username
Scroll to the bottom of the file and add **your GitHub username** on a new line.

**Example — before:**
```
# ─────────────────────────────────────────────────────────────────────────────
alice
bob
```

**Example — after (you add your username):**
```
# ─────────────────────────────────────────────────────────────────────────────
alice
bob
yourGitHubUsername
```

> ⚠️ **Important rules:**
> - Add **only your GitHub username** — plain text, no spaces, no `@` symbol.
> - Do **NOT** edit any other file. PRs that modify other files are **automatically closed**.
> - Add **one username per line**.

---

### Step 4 — Commit the Change
Scroll down to the **"Commit changes"** section.

- Leave the default branch as-is (it will be something like `patch-1`).
- Click **"Propose changes"**.

---

### Step 5 — Open a Pull Request
GitHub will take you to the **"Open a pull request"** page.

- Make sure the **base repository** is the original repo and the **base branch** is `main`.
- Click **"Create pull request"**.

---

### Step 6 — Wait for Auto-Merge ⏳
The **GitHub Actions workflow** will run automatically and:

| # | Action |
|---|--------|
| 1 | ✅ Validate that only `readers.txt` was changed |
| 2 | ✅ Extract your GitHub username from the diff |
| 3 | ✅ Create the **Readers** team (if it doesn't exist) with read-only permission |
| 4 | ✅ Make the repository **public** (fixes any 404) |
| 5 | ✅ Add **you** to the Readers team |
| 6 | ✅ Auto-merge your PR |
| 7 | ✅ Post a welcome comment on your PR |

You will see a comment like this on your PR:

> ✅ **Welcome, @yourGitHubUsername!** You have been added to the **Readers** team and now have read-only access to this repository.

---

## ❌ What Happens if You Break the Rules?

| Violation | What the bot does |
|-----------|------------------|
| Modified a file other than `readers.txt` | PR is **automatically closed** with an explanation comment |
| No valid username found in the diff | PR is **automatically closed** with an explanation comment |
| Username contains invalid characters | PR is **automatically closed** |

If your PR is closed, simply open a new one following the steps above correctly.

---

## 🔒 What Access Means

As a member of the **Readers** team you can:

| ✅ Allowed | ❌ Not Allowed |
|-----------|---------------|
| View all files and code | Push / commit changes |
| **Fork** the repository | Delete branches or tags |
| Open issues (if enabled) | Modify any file in this repo |
| Download releases | Merge pull requests |

> ℹ️ **About cloning:** Because the repository is public, GitHub allows anyone to clone it — this cannot be restricted on public repositories. If you only need to read/browse code, use the GitHub UI or fork the repo to your own account.

---

## 🛠️ Admin / Repo Owner Setup (One-Time)

> **Users can skip this section.** This is only for the repository owner.

1. **Create a Personal Access Token (PAT)** with the following scopes:
   - `admin:org` — to create teams and manage memberships
   - `repo` — to merge PRs as admin

2. **Add it as a repository secret** named `ORG_ADMIN_TOKEN`:
   ```
   Settings → Secrets and variables → Actions → New repository secret
   ```

3. **Enable branch protection** on `main` (recommended):
   ```
   Settings → Branches → Add rule → Require pull request reviews before merging
   ```
   This prevents direct pushes to `main` by anyone.

4. The workflow file lives at:
   ```
   .github/workflows/add-readers.yml
   ```
