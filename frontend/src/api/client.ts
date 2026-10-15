import axios, { AxiosError, type AxiosInstance } from 'axios';
import type {
  ApiError,
  BudgetWithProgress,
  Category,
  DashboardSummary,
  MessageResponse,
  MonthlyReport,
  CategoryReport,
  TrendReport,
  SummaryReport,
  PaginatedResponse,
  Token,
  Transaction,
  User,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const client: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Attach JWT to every request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('ff_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401.
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      const here = window.location.pathname;
      if (!here.startsWith('/login') && !here.startsWith('/register')) {
        localStorage.removeItem('ff_token');
        localStorage.removeItem('ff_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export function extractError(err: unknown, fallback = 'Something went wrong'): string {
  if (axios.isAxiosError<ApiError>(err)) {
    const data = err.response?.data;
    if (data?.detail) return data.detail;
    if (typeof data === 'string') return data;
    if (err.message) return err.message;
  }
  if (err instanceof Error) return err.message;
  return fallback;
}

// ---- Auth ----
export const authApi = {
  register: (data: { name: string; email: string; password: string; password_confirm: string }) =>
    client.post<User>('/auth/register', data).then((r) => r.data),
  login: (data: { email: string; password: string }) =>
    client.post<Token>('/auth/login', data).then((r) => r.data),
  logout: () => client.post('/auth/logout').then((r) => r.data),
  me: () => client.get<User>('/auth/me').then((r) => r.data),
};

// ---- Users ----
export const usersApi = {
  getMe: () => client.get<User>('/users/me').then((r) => r.data),
  updateMe: (data: { name?: string; email?: string }) =>
    client.put<User>('/users/me', data).then((r) => r.data),
  changePassword: (data: { current_password: string; new_password: string; new_password_confirm: string }) =>
    client.put<MessageResponse>('/users/me/password', data).then((r) => r.data),
};

// ---- Categories ----
export const categoriesApi = {
  list: (type?: 'income' | 'expense') =>
    client.get<Category[]>('/categories', { params: type ? { type } : {} }).then((r) => r.data),
  create: (data: { name: string; type: 'income' | 'expense'; color?: string; icon?: string }) =>
    client.post<Category>('/categories', data).then((r) => r.data),
  update: (id: number, data: Partial<{ name: string; type: 'income' | 'expense'; color: string; icon: string }>) =>
    client.put<Category>(`/categories/${id}`, data).then((r) => r.data),
  delete: (id: number) => client.delete<MessageResponse>(`/categories/${id}`).then((r) => r.data),
};

// ---- Transactions ----
export interface TransactionFilters {
  type?: 'income' | 'expense';
  category_id?: number;
  search?: string;
  start_date?: string;
  end_date?: string;
  sort_by?: 'transaction_date' | 'amount' | 'created_at';
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export const transactionsApi = {
  list: (filters: TransactionFilters = {}) =>
    client.get<PaginatedResponse<Transaction>>('/transactions', { params: filters }).then((r) => r.data),
  get: (id: number) => client.get<Transaction>(`/transactions/${id}`).then((r) => r.data),
  create: (data: {
    type: 'income' | 'expense';
    amount: string;
    category_id?: number | null;
    description?: string | null;
    transaction_date: string;
  }) => client.post<Transaction>('/transactions', data).then((r) => r.data),
  update: (id: number, data: Partial<{
    type: 'income' | 'expense';
    amount: string;
    category_id: number | null;
    description: string | null;
    transaction_date: string;
  }>) => client.put<Transaction>(`/transactions/${id}`, data).then((r) => r.data),
  delete: (id: number) => client.delete(`/transactions/${id}`).then((r) => r.data),
};

// ---- Budgets ----
export const budgetsApi = {
  list: () => client.get<BudgetWithProgress[]>('/budgets').then((r) => r.data),
  create: (data: { category_id: number; year: number; month: number; amount: string }) =>
    client.post<BudgetWithProgress>('/budgets', data).then((r) => r.data),
  update: (id: number, data: { amount: string }) =>
    client.put<BudgetWithProgress>(`/budgets/${id}`, data).then((r) => r.data),
  delete: (id: number) => client.delete<MessageResponse>(`/budgets/${id}`).then((r) => r.data),
};

// ---- Dashboard ----
export const dashboardApi = {
  summary: () => client.get<DashboardSummary>('/dashboard/summary').then((r) => r.data),
};

// ---- Reports ----
export const reportsApi = {
  monthly: (params: { start_date?: string; end_date?: string } = {}) =>
    client.get<MonthlyReport>('/reports/monthly', { params }).then((r) => r.data),
  categories: (params: { start_date?: string; end_date?: string } = {}) =>
    client.get<CategoryReport>('/reports/categories', { params }).then((r) => r.data),
  trends: (params: { start_date?: string; end_date?: string } = {}) =>
    client.get<TrendReport>('/reports/trends', { params }).then((r) => r.data),
  summary: (params: { start_date?: string; end_date?: string } = {}) =>
    client.get<SummaryReport>('/reports/summary', { params }).then((r) => r.data),
};

// ---- Health ----
export const healthApi = {
  check: () => axios.get('/health').then((r) => r.data),
};

export default client;
