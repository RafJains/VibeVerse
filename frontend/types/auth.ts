export type UserRole =
  | "guest"
  | "normal_user"
  | "community_owner"
  | "moderator"
  | "verified_user"
  | "admin"
  | "super_admin";

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SignupPayload {
  email: string;
  username: string;
  password: string;
}

export interface LoginPayload {
  email_or_username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
