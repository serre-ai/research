'use client';

import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { clsx } from 'clsx';
import { forwardRef } from 'react';

export const TooltipProvider = TooltipPrimitive.Provider;
export const Tooltip = TooltipPrimitive.Root;
export const TooltipTrigger = TooltipPrimitive.Trigger;

export const TooltipContent = forwardRef<
  HTMLDivElement,
  TooltipPrimitive.TooltipContentProps
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={clsx(
      'z-50 overflow-hidden border border-border bg-bg-elevated px-3 py-1.5',
      'font-mono text-xs text-text-secondary',
      'animate-in fade-in-0 zoom-in-95',
      className,
    )}
    {...props}
  />
));
TooltipContent.displayName = 'TooltipContent';
