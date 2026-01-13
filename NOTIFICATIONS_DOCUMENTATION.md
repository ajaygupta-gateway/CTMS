# CTMS Notification System Documentation

## 1. Overview

The CTMS Notification System provides real-time updates to users about task assignments, status changes, and approaching deadlines. It uses a hybrid approach combining **WebSockets** (for real-time delivery) and **Database Queuing** (for offline reliable delivery).

**Core Features:**
- **Real-time Updates**: Instant notifications via WebSockets.
- **Offline Queuing**: Notifications are stored and delivered when the user reconnects.
- **Status Tracking**: Tracks delivery status (`is_delivered`) and read status (`read`).
- **Deadline Warnings**: Automated alerts 1 hour before task deadlines.
- **Interactive UI**: Real-time unread count, browser notifications, and click-to-navigate.

---

## 2. Architecture

### 2.1 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Protocol** | WebSockets (via Django Channels) | Real-time bi-directional communication |
| **Broker** | Redis | Message broker for Channels and Celery |
| **Server** | Daphne (ASGI) | Async server for handling WebSocket connections |
| **Background** | Celery + Celery Beat | Scheduled tasks (deadline checks, cleanup) |
| **Frontend** | Native WebSocket API | Client-side connection management |

### 2.2 Data Flow

1.  **Event Trigger** (e.g., Task Update or Celery Task) -> **Signal/Service**
2.  **Notification Creation**: Saved to DB with `is_delivered=False`.
3.  **Channel Layer**: Message sent to user's specific group (`notifications_{user_id}`).
4.  **Consumer (Server)**:
    *   *If Connected*: Receives message, sends to WebSocket, marks `is_delivered=True`.
    *   *If Offline*: Message is ignored (discarded by Redis), remains `is_delivered=False` in DB.
5.  **Reconnection**:
    *   User connects -> `Consumer.connect()`
    *   Fetches all `is_delivered=False` notifications from DB.
    *   Sends them to WebSocket and marks `is_delivered=True`.

---

## 3. Backend Implementation

### 3.1 Models (`apps/notifications/models.py`)

Extended `Notification` model with:
-   `notification_type`: `status_change`, `task_assigned`, `task_unassigned`, `deadline_warning`
-   `is_delivered`: Boolean flag for offline queuing logic.
-   `read`: Read/unread status.

### 3.2 WebSocket Consumer (`apps/notifications/consumers.py`)

**`NotificationConsumer`**:
-   **Authentication**: Validates JWT token from query params (`?token=...`).
-   **Grouping**: Adds user to `notifications_{user_id}` channel group.
-   **Offline Handling**: On `connect()`, retrieves and sends pending notifications.
-   **Delivery Tracking**: Updates `is_delivered` status upon successful send.

### 3.3 Signals (`apps/notifications/signals.py`)

-   **`post_save` on Task**:
    -   Detects status changes or new assignments.
    -   Creates `Notification`.
    -   Sends to Channel Layer (does *not* mark delivered; leaves that to Consumer).

### 3.4 Background Tasks (`apps/notifications/tasks.py`)

-   **`check_deadline_warnings`**:
    -   Runs every 10 minutes (via Celery Beat).
    -   Finds tasks due in < 1 hour.
    -   Sends warning if not already sent.
-   **`cleanup_old_notifications`**:
    -   Runs daily.
    -   Deletes read notifications older than 30 days.

---

## 4. Frontend Implementation

### 4.1 WebSocket Service (`lib/websocket.ts`)

**`WebSocketService` Singleton**:
-   **Connection Management**: Handles `connect()`, `disconnect()`, and auto-reconnect with exponential backoff.
-   **Event Handling**: Publishes incoming messages to subscribers.
-   **Browser Notifications**: Requests permission and shows system notifications if granted.

### 4.2 State Management (`context/NotificationContext.tsx`)

**`NotificationProvider`**:
-   Global state for `notifications` list and `unreadCount`.
-   Initializes WebSocket connection on login.
-   Optimistic UI updates for "Mark as Read".
-   Deduplicates incoming notifications to prevent UI glitches.

### 4.3 Components

-   **`NotificationBell`**:
    -   Visual indicator with animated badge.
    -   Shows pulse animation for unread items.
-   **`NotificationPanel`**:
    -   Dropdown list of recent notifications.
    -   distinct icons for different notification types.
    -   "Mark all as read" functionality.
    -   Click-to-navigate to relevant task.

---

## 5. API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notifications/` | List current user's notifications. |
| `GET` | `/api/notifications/unread_count/` | Get usage count of unread items. |
| `POST` | `/api/notifications/{id}/mark_read/` | Mark a specific notification as read. |
| `POST` | `/api/notifications/mark_all_read/` | Mark all notifications as read. |

### WebSocket Protocol

**URL**: `ws://<host>/ws/notifications/?token=<jwt_access_token>`

**Server -> Client Events**:
```json
{
  "type": "notification",
  "notification": {
    "id": 1,
    "message": "Task 'Fix Login' status changed to In Progress",
    "notification_type": "status_change",
    "task_id": 10,
    "created_at": "2024-01-13T10:00:00Z",
    "read": false
  }
}
```

**Client -> Server Actions**:
```json
// Mark as read
{
  "action": "mark_read",
  "notification_id": 1
}

// Mark all as read
{
  "action": "mark_all_read"
}
```

---

## 6. Setup & Deployment Recommendations

### Prerequisites
-   **Redis** (Required for Channel Layer and Celery).
-   **PostgreSQL** (Recommended for production).

### Backend Startup
1.  **Migrations**: `python manage.py migrate`
2.  **ASGI Server**: `daphne -b 0.0.0.0 -p 8000 config.asgi:application`
    *   *Note*: Do not use `gunicorn` alone; use `daphne` or `uvicorn` for WebSocket support.
3.  **Celery Worker**: `celery -A config worker -l info`
4.  **Celery Beat**: `celery -A config beat -l info`

### Frontend Configuration
No special configuration needed. `WebSocketService` automatically determines the WS URL based on the current `window.location`.
