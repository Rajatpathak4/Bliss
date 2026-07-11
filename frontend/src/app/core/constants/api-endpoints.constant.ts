/**
 * ============================================================
 *  API ENDPOINTS — every backend path in one place.
 *  Full URL = environment.apiBaseUrl + <path>.
 * ============================================================
 */

export enum ApiMethod {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE"
}

export const API_ENDPOINTS = {
  // ---- Auth ----
  SIGNUP: '/auth/signup',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',

  // ---- Notifications ----
  ALERTS: '/get_notifications',
  MARK_NOTIFICATION_READ: '/mark_notification_read',
  MARK_ALL_READ: '/mark_all_notifications_read',

  // ---- Clients (users) ----
  GET_USER_TABLE_DATA: '/get_user_table_data', 
  USER_MODAL_DATA: '/user_modal_data',         
  ADD_USER_DATA: '/add_user_data',            
  UPDATE_USER_DATA: '/update_user_data',      
  DELETE_USER_DATA: '/delete_user_excel',      

  // ---- Excel upload ----
  UPLOAD_USER_EXCEL: '/upload_user_excel',     

  // ---- Dashboard ----
  GET_ACTIVE_CLIENT: '/get_active_client',    
  GET_PREMIUM_STATS: '/get_premium_stats', 
  
  GET_DASHBOARD_CHARTS:'/chart_data',
  
} as const;

export type ApiEndpoint = (typeof API_ENDPOINTS)[keyof typeof API_ENDPOINTS];
