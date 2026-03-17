export const AUTH_ROUTES = {
  AUTH_PAGE: '/auth',
  HOME: '/',
} as const;

export const OAUTH_PROVIDERS = {
  GOOGLE: 'google',
} as const;

export type OAuthProvider = typeof OAUTH_PROVIDERS[keyof typeof OAUTH_PROVIDERS];
