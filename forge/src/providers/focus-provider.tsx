'use client';

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from 'react';
import type { ReactNode, MutableRefObject } from 'react';

export interface KeyHint {
  key: string;
  label: string;
}

export interface PanelRegistration {
  id: string;
  order: number;
  itemCount: number;
  keyHints?: KeyHint[];
  onActivateItem?: (index: number) => void;
  onEscape?: () => void;
}

interface FocusState {
  activePanelId: string | null;
  activeItemIndex: number;
}

interface FocusContextType {
  activePanelId: string | null;
  activeItemIndex: number;
  isPanelActive: (panelId: string) => boolean;
  isItemActive: (panelId: string, itemIndex: number) => boolean;
  registerPanel: (reg: PanelRegistration) => () => void;
  updatePanel: (id: string, updates: Partial<Omit<PanelRegistration, 'id'>>) => void;
  focusPanel: (panelId: string) => void;
  focusItem: (panelId: string, itemIndex: number) => void;
  focusFirstAfter: (minOrder: number) => void;
  activeKeyHints: KeyHint[];
  globalKeyHints: KeyHint[];
}

const GLOBAL_HINTS: KeyHint[] = [
  { key: 'Tab', label: 'Next panel' },
  { key: '↑↓', label: 'Navigate' },
  { key: 'Enter', label: 'Select' },
  { key: 'Esc', label: 'Back' },
];

const FocusContext = createContext<FocusContextType>({
  activePanelId: null,
  activeItemIndex: 0,
  isPanelActive: () => false,
  isItemActive: () => false,
  registerPanel: () => () => {},
  updatePanel: () => {},
  focusPanel: () => {},
  focusItem: () => {},
  focusFirstAfter: () => {},
  activeKeyHints: [],
  globalKeyHints: GLOBAL_HINTS,
});

// Separate context for the keydown handler ref — prevents re-renders on state change
const FocusKeydownContext = createContext<MutableRefObject<(e: KeyboardEvent) => void>>({
  current: () => {},
} as MutableRefObject<(e: KeyboardEvent) => void>);

export function FocusProvider({ children }: { children: ReactNode }) {
  const panelsRef = useRef<Map<string, PanelRegistration>>(new Map());
  const [state, setState] = useState<FocusState>({
    activePanelId: null,
    activeItemIndex: 0,
  });

  const getSortedPanelIds = useCallback((): string[] => {
    return Array.from(panelsRef.current.entries())
      .sort(([, a], [, b]) => a.order - b.order)
      .map(([id]) => id);
  }, []);

  const registerPanel = useCallback((reg: PanelRegistration) => {
    panelsRef.current.set(reg.id, reg);
    // Auto-focus first panel
    setState((prev) => {
      if (prev.activePanelId === null) {
        return { activePanelId: reg.id, activeItemIndex: 0 };
      }
      return prev;
    });
    return () => {
      panelsRef.current.delete(reg.id);
      setState((prev) => {
        if (prev.activePanelId === reg.id) {
          const sorted = Array.from(panelsRef.current.entries())
            .sort(([, a], [, b]) => a.order - b.order);
          return {
            activePanelId: sorted.length > 0 ? sorted[0][0] : null,
            activeItemIndex: 0,
          };
        }
        return prev;
      });
    };
  }, []);

  const updatePanel = useCallback((id: string, updates: Partial<Omit<PanelRegistration, 'id'>>) => {
    const existing = panelsRef.current.get(id);
    if (existing) {
      panelsRef.current.set(id, { ...existing, ...updates });
    }
  }, []);

  const focusPanel = useCallback((panelId: string) => {
    if (panelsRef.current.has(panelId)) {
      setState({ activePanelId: panelId, activeItemIndex: 0 });
    }
  }, []);

  const focusItem = useCallback((panelId: string, itemIndex: number) => {
    if (panelsRef.current.has(panelId)) {
      setState({ activePanelId: panelId, activeItemIndex: itemIndex });
    }
  }, []);

  const focusFirstAfter = useCallback((minOrder: number) => {
    const sorted = Array.from(panelsRef.current.entries())
      .filter(([, reg]) => reg.order >= minOrder)
      .sort(([, a], [, b]) => a.order - b.order);
    if (sorted.length > 0) {
      setState({ activePanelId: sorted[0][0], activeItemIndex: 0 });
    }
  }, []);

  const isPanelActive = useCallback(
    (panelId: string) => state.activePanelId === panelId,
    [state.activePanelId],
  );

  const isItemActive = useCallback(
    (panelId: string, itemIndex: number) =>
      state.activePanelId === panelId && state.activeItemIndex === itemIndex,
    [state.activePanelId, state.activeItemIndex],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const sorted = getSortedPanelIds();
      if (sorted.length === 0) return;

      // Tab / Shift+Tab: cycle panels
      if (e.key === 'Tab') {
        e.preventDefault();
        const idx = state.activePanelId ? sorted.indexOf(state.activePanelId) : -1;
        const next = e.shiftKey
          ? (idx <= 0 ? sorted.length - 1 : idx - 1)
          : (idx >= sorted.length - 1 ? 0 : idx + 1);
        setState({ activePanelId: sorted[next], activeItemIndex: 0 });
        return;
      }

      const panel = state.activePanelId
        ? panelsRef.current.get(state.activePanelId)
        : undefined;
      if (!panel) return;

      if (e.key === 'ArrowDown' || e.key === 'j') {
        e.preventDefault();
        setState((prev) => ({
          ...prev,
          activeItemIndex: Math.min(prev.activeItemIndex + 1, panel.itemCount - 1),
        }));
        return;
      }

      if (e.key === 'ArrowUp' || e.key === 'k') {
        e.preventDefault();
        setState((prev) => ({
          ...prev,
          activeItemIndex: Math.max(prev.activeItemIndex - 1, 0),
        }));
        return;
      }

      if (e.key === 'Enter') {
        e.preventDefault();
        panel.onActivateItem?.(state.activeItemIndex);
        return;
      }

      if (e.key === 'Escape') {
        panel.onEscape?.();
        return;
      }
    },
    [state, getSortedPanelIds],
  );

  const handleKeyDownRef = useRef(handleKeyDown);
  handleKeyDownRef.current = handleKeyDown;

  const activePanel = state.activePanelId
    ? panelsRef.current.get(state.activePanelId)
    : undefined;

  return (
    <FocusContext.Provider
      value={{
        activePanelId: state.activePanelId,
        activeItemIndex: state.activeItemIndex,
        isPanelActive,
        isItemActive,
        registerPanel,
        updatePanel,
        focusPanel,
        focusItem,
        focusFirstAfter,
        activeKeyHints: activePanel?.keyHints ?? [],
        globalKeyHints: GLOBAL_HINTS,
      }}
    >
      <FocusKeydownContext.Provider value={handleKeyDownRef}>
        {children}
      </FocusKeydownContext.Provider>
    </FocusContext.Provider>
  );
}

export function useFocus() {
  return useContext(FocusContext);
}

export function useFocusKeydownHandler() {
  return useContext(FocusKeydownContext);
}
