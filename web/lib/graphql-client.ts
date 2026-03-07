import { GraphQLClient } from 'graphql-request';

const GRAPHQL_URL =
  (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/graphql';

let getSessionToken: (() => Promise<string | null>) | null = null;

export function setGraphQLTokenGetter(getter: () => string | undefined) {
  // Wrap sync getter in async for backward compat
  getSessionToken = async () => getter() ?? null;
}

export function setAsyncGraphQLTokenGetter(getter: () => Promise<string | null>) {
  getSessionToken = getter;
}

export async function graphqlClient(): Promise<GraphQLClient> {
  const token = await getSessionToken?.();
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return new GraphQLClient(GRAPHQL_URL, { headers });
}
