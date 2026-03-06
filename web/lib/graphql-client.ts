import { GraphQLClient } from 'graphql-request';

const GRAPHQL_URL =
  (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/graphql';

let getSessionToken: (() => string | undefined) | null = null;

export function setGraphQLTokenGetter(getter: () => string | undefined) {
  getSessionToken = getter;
}

export function graphqlClient(): GraphQLClient {
  const token = getSessionToken?.();
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return new GraphQLClient(GRAPHQL_URL, { headers });
}
