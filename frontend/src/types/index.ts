// Shared types matching the backend Pydantic schemas.

export type TransactionType = 'income' | 'expense';
export type CategoryType = 'income' | 'expense';

export interface User {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Category {
  id: number;
  user_id: number;
  name: string;
  type: CategoryType;
  color: string | null;
  icon: string | null;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  user_id: number;
  type: TransactionType;
  amount: string;
  category_id: number | null;
  category_name: string | null;
  description: string | null;
  transaction_date: string;
  created_at: string;
  updated_at: string;
}

export interface Budget {
  id: number;
  user_id: number;
  category_id: number;
  category_name: string | null;
  year: number;
  month: number;
  amount: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetWithProgress {
  id: number;
  user_id: number;
  category_id: number;
  category_name: string;
  year: number;
  month: number;
  amount: string;
  spent: string;
  remaining: string;
  percent_used: number;
  status: 'ok' | 'warning' | 'exceeded';
}

export interface CategoryBreakdown {
  category_id: number | null;
  category_name: string;
  amount: string;
  percentage: number;
  transaction_count: number;
}

export interface MonthlyPoint {
  month: string;
  income: string;
  expense: string;
  balance: string;
}

export interface RecentTransaction {
  id: number;
  type: string;
  amount: string;
  category_name: string | null;
  description: string | null;
  transaction_date: string;
}

export interface DashboardSummary {
  total_income: string;
  total_expense: string;
  current_balance: string;
  monthly_income: string;
  monthly_expense: string;
  monthly_balance: string;
  income_change_pct: number | null;
  expense_change_pct: number | null;
  recent_transactions: RecentTransaction[];
  expense_breakdown: CategoryBreakdown[];
  monthly_trend: MonthlyPoint[];
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PageMeta;
}

export interface MessageResponse {
  message: string;
}

export interface ApiError {
  error: string;
  detail: string;
  fields?: unknown[];
}

export interface MonthlyReportItem {
  month: string;
  income: string;
  expense: string;
  balance: string;
  savings_rate: number;
}

export interface MonthlyReport {
  items: MonthlyReportItem[];
  total_income: string;
  total_expense: string;
  total_balance: string;
  average_savings_rate: number;
}

export interface CategoryReportItem {
  category_id: number | null;
  category_name: string;
  type: string;
  total: string;
  percentage: number;
  transaction_count: number;
}

export interface CategoryReport {
  items: CategoryReportItem[];
}

export interface TrendPoint {
  period: string;
  income: string;
  expense: string;
  balance: string;
}

export interface TrendReport {
  granularity: string;
  points: TrendPoint[];
}

export interface SummaryReport {
  start_date: string;
  end_date: string;
  income: string;
  expense: string;
  balance: string;
  savings_rate: number;
  highest_expense_category: string | null;
  highest_expense_amount: string | null;
  transaction_count: number;
}
