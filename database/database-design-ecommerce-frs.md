# E-Commerce Platform Database Design
## Based on Functional Requirements Specification

### Database Schema (DBML Format)

```dbml
// ============================================
// USER AUTHENTICATION & MANAGEMENT
// ============================================

users {
  id int pk
  email varchar unique
  password_hash varchar
  first_name varchar
  last_name varchar
  phone varchar
  role_id int > roles.id
  is_active boolean
  is_locked boolean
  email_verified boolean
  created_at datetime
  updated_at datetime
  last_login datetime
}

roles {
  id int pk
  name varchar // 'customer', 'admin', 'manager'
  permissions text
}

login_attempts {
  id int pk
  user_id int > users.id
  ip_address varchar
  attempted_at datetime
  success boolean
}

password_resets {
  id int pk
  user_id int > users.id
  token varchar unique
  expires_at datetime
  used boolean
  created_at datetime
}

user_sessions {
  id int pk
  user_id int > users.id
  session_token varchar unique
  ip_address varchar
  user_agent varchar
  expires_at datetime
  created_at datetime
}

// ============================================
// PRODUCT CATALOG & INVENTORY
// ============================================

categories {
  id int pk
  name varchar
  slug varchar unique
  parent_id int > categories.id
  description text
  image_url varchar
  is_active boolean
  display_order int
}

brands {
  id int pk
  name varchar
  slug varchar unique
  logo_url varchar
  description text
  is_active boolean
}

products {
  id int pk
  sku varchar unique
  name varchar
  slug varchar unique
  description text
  category_id int > categories.id
  brand_id int > brands.id
  base_price decimal
  sale_price decimal
  cost decimal
  weight decimal
  is_active boolean
  is_featured boolean
  created_at datetime
  updated_at datetime
}

product_images {
  id int pk
  product_id int > products.id
  image_url varchar
  alt_text varchar
  is_primary boolean
  display_order int
}

product_inventory {
  id int pk
  product_id int > products.id unique
  quantity int
  reserved_quantity int
  low_stock_threshold int
  track_inventory boolean
  allow_backorder boolean
  updated_at datetime
}

product_attributes {
  id int pk
  product_id int > products.id
  attribute_name varchar // 'size', 'color', 'material'
  attribute_value varchar
}

price_history {
  id int pk
  product_id int > products.id
  old_price decimal
  new_price decimal
  changed_by int > users.id
  changed_at datetime
}

// ============================================
// SHOPPING CART
// ============================================

shopping_carts {
  id int pk
  user_id int > users.id
  session_id varchar // for guest users
  created_at datetime
  updated_at datetime
  expires_at datetime
}

cart_items {
  id int pk
  cart_id int > shopping_carts.id
  product_id int > products.id
  quantity int
  price_at_time decimal
  added_at datetime
  updated_at datetime
}

// ============================================
// ORDERS & ORDER PROCESSING
// ============================================

orders {
  id int pk
  order_number varchar unique
  user_id int > users.id
  status_id int > order_statuses.id
  subtotal decimal
  tax_amount decimal
  shipping_cost decimal
  discount_amount decimal
  total_amount decimal
  currency varchar
  shipping_address_id int > addresses.id
  billing_address_id int > addresses.id
  payment_id int > payments.id
  notes text
  created_at datetime
  updated_at datetime
}

order_statuses {
  id int pk
  status varchar // 'pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
  description text
  is_final boolean
}

order_items {
  id int pk
  order_id int > orders.id
  product_id int > products.id
  product_name varchar // stored for history
  product_sku varchar // stored for history
  quantity int
  unit_price decimal
  discount_amount decimal
  tax_amount decimal
  total_price decimal
}

order_status_history {
  id int pk
  order_id int > orders.id
  status_id int > order_statuses.id
  changed_by int > users.id
  notes text
  created_at datetime
}

order_tracking {
  id int pk
  order_id int > orders.id
  carrier varchar
  tracking_number varchar
  tracking_url varchar
  shipped_at datetime
  delivered_at datetime
  updated_at datetime
}

// ============================================
// PAYMENT PROCESSING
// ============================================

payments {
  id int pk
  order_id int > orders.id
  payment_method_id int > payment_methods.id
  transaction_id varchar unique
  amount decimal
  currency varchar
  status varchar // 'pending', 'completed', 'failed', 'refunded'
  gateway_response text
  processed_at datetime
  created_at datetime
}

payment_methods {
  id int pk
  name varchar // 'credit_card', 'debit_card', 'paypal', 'stripe'
  is_active boolean
}

saved_payment_methods {
  id int pk
  user_id int > users.id
  payment_method_id int > payment_methods.id
  card_last_four varchar
  card_brand varchar
  expiry_month int
  expiry_year int
  is_default boolean
  token varchar // encrypted payment token
  created_at datetime
}

refunds {
  id int pk
  order_id int > orders.id
  payment_id int > payments.id
  amount decimal
  reason text
  status varchar // 'pending', 'approved', 'completed', 'rejected'
  processed_by int > users.id
  refund_transaction_id varchar
  created_at datetime
  completed_at datetime
}

// ============================================
// USER PROFILE & PREFERENCES
// ============================================

user_profiles {
  id int pk
  user_id int > users.id unique
  date_of_birth date
  gender varchar
  newsletter_subscribed boolean
  sms_notifications boolean
  email_notifications boolean
  preferred_currency varchar
  preferred_language varchar
}

addresses {
  id int pk
  user_id int > users.id
  type varchar // 'shipping', 'billing'
  is_default boolean
  full_name varchar
  company varchar
  address_line1 varchar
  address_line2 varchar
  city varchar
  state_province varchar
  postal_code varchar
  country varchar
  phone varchar
}

user_favorites {
  id int pk
  user_id int > users.id
  product_id int > products.id
  added_at datetime
}

recently_viewed {
  id int pk
  user_id int > users.id
  product_id int > products.id
  viewed_at datetime
}

// ============================================
// ADMIN & REPORTING
// ============================================

admin_activity_logs {
  id int pk
  admin_id int > users.id
  action varchar // 'create_product', 'update_order', 'delete_user'
  entity_type varchar // 'product', 'order', 'user'
  entity_id int
  old_values text
  new_values text
  ip_address varchar
  performed_at datetime
}

sales_reports {
  id int pk
  report_date date
  total_orders int
  total_revenue decimal
  total_tax decimal
  total_shipping decimal
  total_refunds decimal
  average_order_value decimal
  generated_at datetime
}

inventory_logs {
  id int pk
  product_id int > products.id
  old_quantity int
  new_quantity int
  change_reason varchar // 'sale', 'return', 'adjustment', 'restock'
  reference_id int // order_id or adjustment_id
  changed_by int > users.id
  changed_at datetime
}

// ============================================
// PROMOTIONS & DISCOUNTS
// ============================================

coupons {
  id int pk
  code varchar unique
  description text
  discount_type varchar // 'percentage', 'fixed_amount'
  discount_value decimal
  minimum_purchase decimal
  usage_limit int
  used_count int
  valid_from datetime
  valid_until datetime
  is_active boolean
}

user_coupons {
  id int pk
  user_id int > users.id
  coupon_id int > coupons.id
  used_at datetime
  order_id int > orders.id
}

// ============================================
// REVIEWS & RATINGS
// ============================================

product_reviews {
  id int pk
  product_id int > products.id
  user_id int > users.id
  order_item_id int > order_items.id
  rating int
  title varchar
  comment text
  is_verified_purchase boolean
  is_approved boolean
  helpful_votes int
  unhelpful_votes int
  created_at datetime
  updated_at datetime
}

review_votes {
  id int pk
  review_id int > product_reviews.id
  user_id int > users.id
  is_helpful boolean
  voted_at datetime
}

// ============================================
// NOTIFICATIONS & COMMUNICATIONS
// ============================================

email_queue {
  id int pk
  user_id int > users.id
  email_type varchar // 'order_confirmation', 'password_reset', 'shipping_update'
  subject varchar
  body text
  status varchar // 'pending', 'sent', 'failed'
  attempts int
  sent_at datetime
  created_at datetime
}

notifications {
  id int pk
  user_id int > users.id
  type varchar
  title varchar
  message text
  is_read boolean
  created_at datetime
  read_at datetime
}
```

### Key Design Features

#### 1. **Authentication & Security**
- Password hashing stored in `password_hash` field
- Login attempt tracking with lockout after 3 failed attempts
- Password reset tokens with expiration
- Session management for persistent carts
- Role-based access control for admin functions

#### 2. **Product Management**
- Comprehensive product catalog with categories and brands
- Real-time inventory tracking with reserved quantities
- Product image gallery support
- Price history tracking for auditing
- Product attributes for variations (size, color, etc.)

#### 3. **Shopping Cart**
- Persistent cart across sessions
- Guest cart support via session_id
- Price snapshot at time of adding to cart

#### 4. **Order Processing**
- Complete order lifecycle tracking
- Order status history for full traceability
- Shipping and tracking integration
- Separate billing and shipping addresses

#### 5. **Payment Processing**
- Multiple payment method support
- Encrypted payment token storage
- Comprehensive refund management
- Transaction logging for auditing

#### 6. **User Experience**
- User profiles with preferences
- Multiple address management
- Favorites and recently viewed products
- Review and rating system

#### 7. **Admin Features**
- Activity logging for all admin actions
- Sales reporting and analytics
- Inventory change tracking
- User management capabilities

#### 8. **Performance Optimizations**
- Indexes on frequently queried fields (email, sku, order_number)
- Separate tables for heavy operations (logs, reports)
- Denormalized fields for performance (order_items stores product name/sku)

#### 9. **Data Validation**
- Unique constraints on email, SKU, order numbers
- Foreign key constraints for referential integrity
- Check constraints can be added for price validation
- Enum-like fields for status management

This design fully addresses all requirements from your FRS document while maintaining scalability and security best practices.
