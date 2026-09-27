# Campus Customs frontend

React 19 + TypeScript + Vite. See the main [README](../README.md) for full setup.

```bash
npm install
npm run dev      # http://localhost:5173 (proxies /api and /media to the backend on :8000)
npm run build    # type-check + production build into dist/
```

Entry: `index.html` → `src/main.tsx` → `src/App.tsx`. Pages are in `src/pages/`, components in `src/components/`, API calls in `src/api.ts`, and styles in `src/index.css`.
