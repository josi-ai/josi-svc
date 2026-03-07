# Descope Frontend Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the custom email/password auth UI with Descope's pre-built auth flow, wire up session management via Descope Next.js SDK, and connect the API key management page.

**Architecture:** Descope AuthProvider wraps the app. Login page renders a Descope Flow component. AuthContext becomes a thin wrapper around Descope hooks. API client reads the session token from Descope. Middleware checks Descope session cookies.

**Tech Stack:** @descope/nextjs-sdk, Next.js 14 App Router, Ant Design, TanStack React Query

**Design Doc:** `docs/plans/2026-03-06-descope-auth-design.md`

---

## Task F1: Install Descope Next.js SDK

**Files:**
- Modify: `web/package.json`

**Step 1: Install the SDK**

```bash
cd web && npm install @descope/nextjs-sdk
```

**Step 2: Verify installation**

```bash
cd web && node -e "require('@descope/nextjs-sdk')"
```
Expected: No error

**Step 3: Commit**

```bash
git add web/package.json web/package-lock.json
git commit -m "feat(web): add @descope/nextjs-sdk dependency"
```

---

## Task F2: Update Root Layout with Descope AuthProvider

**Files:**
- Modify: `web/app/layout.tsx`
- Modify: `web/components/providers.tsx`

**Step 1: Update providers.tsx**

Replace the existing providers file. Remove the old custom `AuthProvider` import and wrap with Descope's `AuthProvider`:

```tsx
'use client';

import { AuthProvider } from '@descope/nextjs-sdk';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SubscriptionProvider } from '@/contexts/SubscriptionContext';
import theme from '@/theme/themeConfig';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider projectId={process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || 'P3AXgK6L8OgCfFSKcrNaA99vVChw'}>
      <AntdRegistry>
        <ConfigProvider theme={theme}>
          <QueryClientProvider client={queryClient}>
            <SubscriptionProvider>
              {children}
            </SubscriptionProvider>
          </QueryClientProvider>
        </ConfigProvider>
      </AntdRegistry>
    </AuthProvider>
  );
}
```

**Step 2: Verify app renders**

```bash
cd web && npm run dev
```
Expected: App starts on port 4000, no errors in console

**Step 3: Commit**

```bash
git add web/components/providers.tsx web/app/layout.tsx
git commit -m "feat(web): wrap app with Descope AuthProvider"
```

---

## Task F3: Replace Login Page with Descope Flow

**Files:**
- Modify: `web/app/(auth)/auth/login/page.tsx`
- Delete: `web/app/(auth)/auth/register/page.tsx`
- Delete: `web/app/(auth)/auth/callback/page.tsx`

**Step 1: Replace login page with Descope Flow component**

```tsx
'use client';

import { Descope } from '@descope/nextjs-sdk';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1a1230 0%, #0f0a1e 50%)',
    }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <Descope
          flowId="sign-up-or-in"
          onSuccess={() => router.push('/dashboard')}
          onError={(e) => console.error('Auth error:', e)}
          theme="dark"
        />
      </div>
    </div>
  );
}
```

The `sign-up-or-in` flow handles both login AND registration — Descope manages the UI.

**Step 2: Delete register and callback pages**

```bash
rm web/app/\(auth\)/auth/register/page.tsx
rm web/app/\(auth\)/auth/callback/page.tsx
```

**Step 3: Delete the server-side refresh route**

```bash
rm web/app/api/auth/refresh/route.ts
```

If the `web/app/api/auth/refresh/` directory is now empty, delete it too:
```bash
rm -rf web/app/api/auth
```

**Step 4: Verify login page renders**

Visit `http://localhost:4000/auth/login` — should show Descope's auth UI.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(web): replace login/register with Descope Flow component"
```

---

## Task F4: Rewrite AuthContext for Descope

**Files:**
- Modify: `web/contexts/AuthContext.tsx`
- Modify: `web/types/auth.ts`

**Step 1: Update auth types**

Replace `web/types/auth.ts`:

```typescript
export interface User {
  id: string;
  descope_id: string;
  email: string;
  name: string;
  phone?: string;
  avatar_url?: string;
  subscription_tier: 'free' | 'explorer' | 'mystic' | 'master';
  roles: string[];
  created_at: string;
}
```

**Step 2: Rewrite AuthContext as a thin Descope wrapper**

Replace `web/contexts/AuthContext.tsx`:

```tsx
'use client';

import { createContext, useContext, useMemo } from 'react';
import { useSession, useUser, useDescope } from '@descope/nextjs-sdk/client';

interface AuthContextType {
  user: {
    id: string;
    descope_id: string;
    email: string;
    name: string;
    phone?: string;
    subscription_tier: string;
    roles: string[];
  } | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  sessionToken: string | undefined;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  sessionToken: undefined,
  logout: async () => {},
});

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isSessionLoading, sessionToken } = useSession();
  const { user: descopeUser, isUserLoading } = useUser();
  const { logout: descopeLogout } = useDescope();

  const user = useMemo(() => {
    if (!isAuthenticated || !descopeUser) return null;

    // Read custom claims from the session token
    let claims: Record<string, any> = {};
    if (sessionToken) {
      try {
        const payload = JSON.parse(atob(sessionToken.split('.')[1]));
        claims = payload;
      } catch {
        // Token parse error — use defaults
      }
    }

    return {
      id: claims.josi_user_id || '',
      descope_id: descopeUser.userId || '',
      email: descopeUser.email || '',
      name: descopeUser.name || '',
      phone: descopeUser.phone || undefined,
      subscription_tier: claims.josi_subscription_tier || 'free',
      roles: claims.josi_roles || ['user'],
    };
  }, [isAuthenticated, descopeUser, sessionToken]);

  const logout = async () => {
    await descopeLogout();
    window.location.href = '/auth/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: isSessionLoading || isUserLoading,
        isAuthenticated,
        sessionToken,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

**Step 3: Wire AuthContextProvider into providers.tsx**

Update `web/components/providers.tsx` — add `AuthContextProvider` inside the Descope `AuthProvider`:

```tsx
import { AuthContextProvider } from '@/contexts/AuthContext';

// Inside the provider tree, after AuthProvider:
<AuthProvider projectId={...}>
  <AntdRegistry>
    <ConfigProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <AuthContextProvider>
          <SubscriptionProvider>
            {children}
          </SubscriptionProvider>
        </AuthContextProvider>
      </QueryClientProvider>
    </ConfigProvider>
  </AntdRegistry>
</AuthProvider>
```

**Step 4: Commit**

```bash
git add web/contexts/AuthContext.tsx web/types/auth.ts web/components/providers.tsx
git commit -m "feat(web): rewrite AuthContext as thin Descope wrapper with custom claims"
```

---

## Task F5: Update API Client to Use Descope Session Token

**Files:**
- Modify: `web/lib/api-client.ts`

**Step 1: Simplify api-client.ts**

The API client no longer manages tokens itself. It accepts a token parameter or reads from a global getter. Replace `web/lib/api-client.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let getSessionToken: (() => string | undefined) | null = null;

export function setTokenGetter(getter: () => string | undefined) {
  getSessionToken = getter;
}

interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  errors?: string[];
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getSessionToken?.();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.detail || error.message || 'Request failed');
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data?: any) =>
    request<T>(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  put: <T>(endpoint: string, data: any) =>
    request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),
};
```

**Step 2: Wire the token getter in AuthContext**

Add to `web/contexts/AuthContext.tsx`, inside the `AuthContextProvider` component (before the return):

```tsx
import { setTokenGetter } from '@/lib/api-client';

// Inside AuthContextProvider, after session hooks:
useEffect(() => {
  setTokenGetter(() => sessionToken);
}, [sessionToken]);
```

Add the `useEffect` import at the top:
```tsx
import { createContext, useContext, useMemo, useEffect } from 'react';
```

**Step 3: Commit**

```bash
git add web/lib/api-client.ts web/contexts/AuthContext.tsx
git commit -m "feat(web): update API client to use Descope session token"
```

---

## Task F6: Update Middleware for Descope

**Files:**
- Modify: `web/middleware.ts`

**Step 1: Update middleware to check Descope session**

Replace `web/middleware.ts`:

```typescript
import { authMiddleware } from '@descope/nextjs-sdk/server';

export default authMiddleware({
  projectId: process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || 'P3AXgK6L8OgCfFSKcrNaA99vVChw',
  redirectUrl: '/auth/login',
  publicRoutes: [
    '/',
    '/auth/login',
    '/chart-calculator',
    '/pricing',
    '/api/v1/webhooks/(.*)',
  ],
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

The Descope middleware automatically:
- Checks for a valid session on protected routes
- Redirects to `/auth/login` if no session
- Passes through public routes

**Step 2: Verify protected routes redirect**

Visit `http://localhost:4000/dashboard` without logging in.
Expected: Redirected to `/auth/login`

**Step 3: Commit**

```bash
git add web/middleware.ts
git commit -m "feat(web): replace custom middleware with Descope authMiddleware"
```

---

## Task F7: Wire API Key Management Page

**Files:**
- Modify: `web/app/(developer)/developer/keys/page.tsx`

**Step 1: Read the current keys page to understand the layout**

Check what's currently in the file and build on it.

**Step 2: Implement the API keys management page**

Replace `web/app/(developer)/developer/keys/page.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { Button, Card, Input, Table, Modal, Typography, Space, Tag, message, Popconfirm } from 'antd';
import { PlusOutlined, CopyOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

const { Title, Text, Paragraph } = Typography;

interface ApiKeyResponse {
  api_key_id: string;
  key_prefix: string;
  name: string;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

interface ApiKeyCreatedResponse {
  api_key_id: string;
  key: string;
  key_prefix: string;
  name: string;
}

export default function ApiKeysPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: keys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiClient.get<ApiKeyResponse[]>('/api/v1/api-keys'),
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => apiClient.post<ApiKeyCreatedResponse>('/api/v1/api-keys', { name }),
    onSuccess: (data) => {
      setCreatedKey(data.data.key);
      setNewKeyName('');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key created');
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.delete(`/api/v1/api-keys/${keyId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key revoked');
    },
  });

  const rotateMutation = useMutation({
    mutationFn: (keyId: string) => apiClient.post<ApiKeyCreatedResponse>(`/api/v1/api-keys/${keyId}/rotate`),
    onSuccess: (data) => {
      setCreatedKey(data.data.key);
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      message.success('API key rotated');
    },
  });

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    {
      title: 'Key',
      dataIndex: 'key_prefix',
      key: 'key_prefix',
      render: (prefix: string) => <Text code>{prefix}...************************</Text>,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Last Used',
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (date: string | null) => date ? new Date(date).toLocaleDateString() : 'Never',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>{active ? 'Active' : 'Revoked'}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ApiKeyResponse) => (
        <Space>
          <Popconfirm title="Rotate this key?" onConfirm={() => rotateMutation.mutate(record.api_key_id)}>
            <Button icon={<SyncOutlined />} size="small">Rotate</Button>
          </Popconfirm>
          <Popconfirm title="Revoke this key?" onConfirm={() => revokeMutation.mutate(record.api_key_id)}>
            <Button icon={<DeleteOutlined />} size="small" danger>Revoke</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>API Keys</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateOpen(true)}>
            Create API Key
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={keys?.data || []}
          loading={isLoading}
          rowKey="api_key_id"
          pagination={false}
        />

        {/* Create Key Modal */}
        <Modal
          title="Create API Key"
          open={isCreateOpen}
          onCancel={() => { setIsCreateOpen(false); setCreatedKey(null); }}
          footer={createdKey ? [
            <Button key="close" onClick={() => { setIsCreateOpen(false); setCreatedKey(null); }}>
              Done
            </Button>,
          ] : [
            <Button key="cancel" onClick={() => setIsCreateOpen(false)}>Cancel</Button>,
            <Button
              key="create"
              type="primary"
              loading={createMutation.isPending}
              onClick={() => createMutation.mutate(newKeyName)}
              disabled={!newKeyName.trim()}
            >
              Create
            </Button>,
          ]}
        >
          {createdKey ? (
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Paragraph type="warning">
                Copy this key now. You will not be able to see it again.
              </Paragraph>
              <Input.TextArea
                value={createdKey}
                readOnly
                autoSize
                style={{ fontFamily: 'monospace' }}
              />
              <Button
                icon={<CopyOutlined />}
                onClick={() => {
                  navigator.clipboard.writeText(createdKey);
                  message.success('Copied to clipboard');
                }}
              >
                Copy to Clipboard
              </Button>
            </Space>
          ) : (
            <Input
              placeholder="Key name (e.g., Production, Staging)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              onPressEnter={() => newKeyName.trim() && createMutation.mutate(newKeyName)}
            />
          )}
        </Modal>
      </Space>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add web/app/\(developer\)/developer/keys/page.tsx
git commit -m "feat(web): wire API key management page to backend endpoints"
```

---

## Task F8: Update Dashboard Header Logout

**Files:**
- Modify: `web/components/layout/dashboard-header.tsx`

**Step 1: Update the header to use the new useAuth hook**

The `useAuth()` hook interface stays the same (`logout()`, `user`), so the header component should work as-is. Verify by checking that:

1. `useAuth()` is imported from `@/contexts/AuthContext`
2. `logout()` is called on the Logout menu item
3. `user.name` or `user.email` is displayed

If the imports match, no changes needed. If the old AuthContext exported differently, update the import.

**Step 2: Verify logout works**

Log in → click user dropdown → Logout → should redirect to `/auth/login`

**Step 3: Commit (only if changes were made)**

```bash
git add web/components/layout/dashboard-header.tsx
git commit -m "feat(web): verify dashboard header works with Descope auth"
```

---

## Task F9: Add Environment Variable

**Files:**
- Create or modify: `web/.env.local` (or `.env`)

**Step 1: Add Descope project ID env var**

```
NEXT_PUBLIC_DESCOPE_PROJECT_ID=P3AXgK6L8OgCfFSKcrNaA99vVChw
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Step 2: Commit .env.example (not .env.local)**

Create `web/.env.example`:
```
NEXT_PUBLIC_DESCOPE_PROJECT_ID=your-descope-project-id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
git add web/.env.example
git commit -m "config(web): add Descope env var example"
```

---

## Summary

### Created
- `web/.env.example`

### Modified
- `web/package.json` (add @descope/nextjs-sdk)
- `web/components/providers.tsx` (Descope AuthProvider)
- `web/app/(auth)/auth/login/page.tsx` (Descope Flow)
- `web/contexts/AuthContext.tsx` (Descope hooks wrapper)
- `web/lib/api-client.ts` (token from Descope)
- `web/middleware.ts` (Descope authMiddleware)
- `web/types/auth.ts` (updated User type)
- `web/app/(developer)/developer/keys/page.tsx` (API key CRUD)
- `web/.env.example`

### Deleted
- `web/app/(auth)/auth/register/page.tsx`
- `web/app/(auth)/auth/callback/page.tsx`
- `web/app/api/auth/refresh/route.ts`
