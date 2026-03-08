'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export type SubscriptionTier = 'free' | 'explorer' | 'mystic' | 'master';

export interface TierLimits {
  charts: number;
  ai_interpretations: number;
  consultations: number;
}

const TIER_LIMITS: Record<SubscriptionTier, TierLimits> = {
  free: { charts: 3, ai_interpretations: 1, consultations: 0 },
  explorer: { charts: 25, ai_interpretations: 10, consultations: 2 },
  mystic: { charts: 100, ai_interpretations: 50, consultations: 10 },
  master: { charts: Infinity, ai_interpretations: Infinity, consultations: Infinity },
};

interface UsageData {
  charts: number;
  ai_interpretations: number;
  consultations: number;
}

interface SubscriptionState {
  tier: SubscriptionTier;
  limits: TierLimits;
  usage: UsageData;
}

interface SubscriptionContextType extends SubscriptionState {
  canUseFeature: (feature: keyof TierLimits) => boolean;
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export function SubscriptionProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [state, setState] = useState<SubscriptionState>({
    tier: 'free',
    limits: TIER_LIMITS.free,
    usage: { charts: 0, ai_interpretations: 0, consultations: 0 },
  });

  useEffect(() => {
    if (isAuthenticated && user) {
      const tier = ((user.subscription_tier_name || user.subscription_tier || 'Free').toLowerCase() as SubscriptionTier) || 'free';
      setState((prev) => ({
        ...prev,
        tier,
        limits: TIER_LIMITS[tier],
      }));
    }
  }, [user, isAuthenticated]);

  const canUseFeature = (feature: keyof TierLimits): boolean => {
    return state.usage[feature] < state.limits[feature];
  };

  return (
    <SubscriptionContext.Provider value={{ ...state, canUseFeature }}>
      {children}
    </SubscriptionContext.Provider>
  );
}

export function useSubscription(): SubscriptionContextType {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
}
