import { Pool } from 'pg';

/**
 * Database Helper for E2E Testing
 * Connects to PostgreSQL/SQLite to verify data changes in real-time
 */

export class DatabaseHelper {
  private pool: Pool | null = null;
  private useSQLite: boolean = false;

  constructor() {
    // Check if using PostgreSQL or SQLite
    this.useSQLite = process.env.USE_POSTGRES !== 'true';
  }

  /**
   * Connect to database
   */
  async connect() {
    if (this.pool) return; // Already connected

    if (!this.useSQLite) {
      this.pool = new Pool({
        host: process.env.POSTGRES_HOST || 'localhost',
        port: parseInt(process.env.POSTGRES_PORT || '5432'),
        database: process.env.POSTGRES_DB || 'smartgriev',
        user: process.env.POSTGRES_USER || 'postgres',
        password: process.env.POSTGRES_PASSWORD || 'postgres',
      });

      // Test connection
      try {
        await this.pool.query('SELECT 1');
        console.log('✓ Database connected successfully');
      } catch (error) {
        console.error('✗ Database connection failed:', error);
        throw error;
      }
    }
  }

  /**
   * Execute SQL query
   */
  async query(sql: string, params: any[] = []) {
    if (this.useSQLite) {
      // For SQLite, we'll use Django admin API instead
      console.warn('SQLite mode: Use API calls for data verification');
      return null;
    }
    
    if (!this.pool) throw new Error('Database pool not initialized');
    const result = await this.pool.query(sql, params);
    return result.rows;
  }

  /**
   * Get user by email
   */
  async getUserByEmail(email: string) {
    const result = await this.query(
      'SELECT id, email, mobile, first_name, last_name, is_active FROM authentication_user WHERE email = $1',
      [email]
    );
    return result && result.length > 0 ? result[0] : null;
  }

  /**
   * Get latest complaint by user
   */
  async getLatestComplaintByUser(userId: number) {
    const result = await this.query(
      `SELECT c.id, c.title, c.description, c.status, c.priority, c.category_id, 
              c.department_id, c.created_at, c.incident_latitude, c.incident_longitude
       FROM complaints_complaint c
       WHERE c.user_id = $1
       ORDER BY c.created_at DESC
       LIMIT 1`,
      [userId]
    );
    return result && result.length > 0 ? result[0] : null;
  }

  /**
   * Get complaint by ID with full details
   */
  async getComplaintById(complaintId: number) {
    const result = await this.query(
      `SELECT c.*, d.name as department_name, cat.name as category_name,
              u.email as user_email, u.first_name || ' ' || u.last_name as user_name
       FROM complaints_complaint c
       LEFT JOIN complaints_department d ON c.department_id = d.id
       LEFT JOIN complaints_complaintcategory cat ON c.category_id = cat.id
       LEFT JOIN authentication_user u ON c.user_id = u.id
       WHERE c.id = $1`,
      [complaintId]
    );
    return result && result.length > 0 ? result[0] : null;
  }

  /**
   * Get complaint media files
   */
  async getComplaintMedia(complaintId: number) {
    return await this.query(
      'SELECT * FROM complaints_complaintmedia WHERE complaint_id = $1',
      [complaintId]
    );
  }

  /**
   * Get chat logs for user
   */
  async getChatLogs(userId: number, limit: number = 10) {
    return await this.query(
      `SELECT cl.*, cs.session_id
       FROM chatbot_chatlog cl
       JOIN chatbot_chatsession cs ON cl.session_id = cs.id
       WHERE cl.user_id = $1
       ORDER BY cl.created_at DESC
       LIMIT $2`,
      [userId, limit]
    );
  }

  /**
   * Get notifications for user
   */
  async getNotifications(userId: number) {
    return await this.query(
      `SELECT * FROM notifications_notification
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );
  }

  /**
   * Get user activity logs
   */
  async getUserActivity(userId: number, limit: number = 20) {
    return await this.query(
      `SELECT * FROM analytics_useractivity
       WHERE user_id = $1
       ORDER BY created_at DESC
       LIMIT $2`,
      [userId, limit]
    );
  }

  /**
   * Get OTP verification record
   */
  async getOTPVerification(email: string) {
    const result = await this.query(
      `SELECT * FROM authentication_otpverification
       WHERE email = $1
       ORDER BY created_at DESC
       LIMIT 1`,
      [email]
    );
    return result && result.length > 0 ? result[0] : null;
  }

  /**
   * Count total complaints
   */
  async getComplaintCount() {
    const result = await this.query('SELECT COUNT(*) as count FROM complaints_complaint');
    return result ? result[0].count : 0;
  }

  /**
   * Count complaints by status
   */
  async getComplaintsByStatus(status: string) {
    const result = await this.query(
      'SELECT COUNT(*) as count FROM complaints_complaint WHERE status = $1',
      [status]
    );
    return result ? result[0].count : 0;
  }

  /**
   * Get audit trail for complaint
   */
  async getAuditTrail(complaintId: number) {
    return await this.query(
      `SELECT * FROM complaints_audittrail
       WHERE complaint_id = $1
       ORDER BY timestamp DESC`,
      [complaintId]
    );
  }

  /**
   * Clean up test data (use with caution!)
   */
  async cleanupTestData(testEmail: string) {
    const users = await this.getUserByEmail(testEmail);
    if (users && users.length > 0) {
      const userId = users[0].id;
      
      // Delete in order of dependencies
      await this.query('DELETE FROM analytics_useractivity WHERE user_id = $1', [userId]);
      await this.query('DELETE FROM notifications_notification WHERE user_id = $1', [userId]);
      await this.query('DELETE FROM chatbot_chatlog WHERE user_id = $1', [userId]);
      await this.query('DELETE FROM complaints_complaint WHERE user_id = $1', [userId]);
      await this.query('DELETE FROM authentication_otpverification WHERE email = $1', [testEmail]);
      await this.query('DELETE FROM authentication_user WHERE id = $1', [userId]);
      
      console.log(`✅ Cleaned up test data for: ${testEmail}`);
    }
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.pool) {
      await this.pool.end();
    }
  }

  /**
   * Get database statistics
   */
  async getStats() {
    if (this.useSQLite) {
      return { message: 'SQLite mode - Use API for stats' };
    }

    const users = await this.query('SELECT COUNT(*) as count FROM authentication_user');
    const complaints = await this.query('SELECT COUNT(*) as count FROM complaints_complaint');
    const chatLogs = await this.query('SELECT COUNT(*) as count FROM chatbot_chatlog');
    const notifications = await this.query('SELECT COUNT(*) as count FROM notifications_notification');

    return {
      users: users ? users[0].count : 0,
      complaints: complaints ? complaints[0].count : 0,
      chatLogs: chatLogs ? chatLogs[0].count : 0,
      notifications: notifications ? notifications[0].count : 0,
    };
  }
}

export const db = new DatabaseHelper();
