# Emotion AI — Frontend

React + TypeScript + Vite + Tailwind CSS frontend for the emotion recognition demo.

## Prerequisites

- Node.js >= 18
- Backend running at `http://localhost:8000` (FastAPI + Celery worker + Redis)

## Setup

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The dev server runs on `http://localhost:3000` (the same origin allowed by the backend's CORS config).

## Build

```bash
npm run build
npm run preview   # serve the production build
```

## Configuration

Create a `.env.local` file in the `frontend/` directory:

```
VITE_API_URL=http://localhost:8000
```

By default the client targets `http://localhost:8000` if no value is set.

## Structure

```
src/
  api/             # axios client + per-endpoint helpers
  components/
    common/        # shared widgets (FileUpload, LoadingRings, ModelSelector, StatTile)
    gallery/       # gallery card
    layout/        # Layout + Navbar + Footer
    models/        # ModelCard, ModelSchema, ConfusionMatrixStub, PerformanceStub
    process/       # Photo/Video result views
    ui/            # design-system primitives (Button, Card, Badge, Tabs, ...)
  data/            # static data (model specs, demo gallery items)
  pages/           # one component per route
  types/           # API + domain types
  utils/           # download helpers
```

## Routes

| Path | Component | Notes |
|---|---|---|
| `/` | HomePage | Hero, three nav cards, "How it works", stat tiles |
| `/models` | ModelsPage | 2x2 grid of architectures |
| `/models/:id` | ModelDetailPage | Schema, specs, tabs (metrics / performance / description) |
| `/process` and `/process/photo` | ProcessPhotoPage | Upload + photo result |
| `/process/video` | ProcessVideoPage | Upload + video result + downloadable statistics |
| `/gallery` | GalleryPage | Demo gallery with photo/video filter |
| `/gallery/:id` | GalleryDetailPage | Single demo item |

## Stubs that need real assets

Marked with comments inside files. Replace when ready:

- `data/models.ts` — accuracy / inference times / weights are placeholders
- `components/models/ConfusionMatrixStub.tsx` — synthetic confusion matrix
- `components/models/PerformanceStub.tsx` — synthetic accuracy curve and benchmark table
- `components/models/ModelSchema.tsx` — simplified block diagrams
- `data/gallery.ts` and `pages/GalleryDetailPage.tsx` — gradient placeholders instead of real media
- `public/stubs/` — drop final media files here

## Backend mapping

The backend currently exposes three model keys (`convnext`, `swin`, `se_resnet`). The frontend exposes four (`resnet_50`, `efficientnet_b3`, `convnext`, `swin`). The mapping lives in `src/types/api.ts` (`MODEL_TO_BACKEND`). Update it once the backend supports the additional architectures.
