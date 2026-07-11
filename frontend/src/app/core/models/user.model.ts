export interface AuthUser {
  id: number;
  fullName: string;
  email: string;
  phone_number: string;
  company: string;
  role: string;
  location: string;
  avatarInitials: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  fullName: string;
  email: string;
  password: string;
}

/** Normalized auth result used throughout the app. */
export interface AuthResponse {
  token: string;
  user: AuthUser;
}

/**
 * Raw response shape returned by the FastAPI /login and /signup endpoints.
 * Field names are optional so this tolerates either `access_token`
 * (OAuth2 style) or `token`. Adjust here if your backend differs.
 */
export interface AuthApiResponse {
  access_token?: string;
  token?: string;
  token_type?: string;
  user?: AuthUser;
}
