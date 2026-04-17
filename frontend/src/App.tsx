import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import ModelsPage from './pages/ModelsPage';
import ModelDetailPage from './pages/ModelDetailPage';
import ProcessPhotoPage from './pages/ProcessPhotoPage';
import ProcessVideoPage from './pages/ProcessVideoPage';
import GalleryPage from './pages/GalleryPage';
import GalleryDetailPage from './pages/GalleryDetailPage';
import NotFoundPage from './pages/NotFoundPage';
import { ErrorBoundary } from './components/common/ErrorBoundary';

export default function App() {
  const location = useLocation();
  return (
    <Layout>
      {/*
        Специально без mode="wait": при быстрой навигации этот режим может
        «зависнуть», ожидая завершения exit-анимации предыдущей страницы,
        и оставить содержимое пустым. Боундари ниже страхует от исключений
        в рендере любой страницы — он гарантированно показывает UI, а не
        белый экран.
      */}
      <ErrorBoundary resetKey={location.pathname}>
        <AnimatePresence initial={false}>
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<HomePage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/models/:id" element={<ModelDetailPage />} />
            <Route path="/process" element={<ProcessPhotoPage />} />
            <Route path="/process/photo" element={<ProcessPhotoPage />} />
            <Route path="/process/video" element={<ProcessVideoPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/gallery/:id" element={<GalleryDetailPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </AnimatePresence>
      </ErrorBoundary>
    </Layout>
  );
}
