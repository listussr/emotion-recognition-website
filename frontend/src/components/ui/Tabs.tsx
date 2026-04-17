import { useState, type ReactNode } from 'react';
import { motion } from 'framer-motion';

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
}

interface TabsProps {
  items: TabItem[];
  defaultId?: string;
}

export function Tabs({ items, defaultId }: TabsProps) {
  const [activeId, setActiveId] = useState(defaultId ?? items[0]?.id);
  const active = items.find((i) => i.id === activeId) ?? items[0];

  return (
    <div>
      <div className="flex gap-1 border-b border-line mb-6 overflow-x-auto">
        {items.map((item) => {
          const isActive = item.id === activeId;
          return (
            <button
              key={item.id}
              onClick={() => setActiveId(item.id)}
              className={`relative px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                isActive ? 'text-ink' : 'text-ink-muted hover:text-ink'
              }`}
            >
              {item.label}
              {isActive && (
                <motion.div
                  layoutId="tab-underline"
                  className="absolute -bottom-px left-0 right-0 h-[2px] bg-brand-gradient rounded-full"
                />
              )}
            </button>
          );
        })}
      </div>
      <motion.div
        key={active?.id}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {active?.content}
      </motion.div>
    </div>
  );
}
