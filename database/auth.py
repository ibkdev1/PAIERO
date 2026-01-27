"""
Authentication Module
User authentication and session management
"""

import hashlib
import os
from datetime import datetime
from typing import Optional, Dict
from database.connection import DatabaseConnection


class AuthManager:
    """Manage user authentication and sessions"""

    # Current logged-in user session
    current_user: Optional[Dict] = None

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 with salt

        Args:
            password: Plain text password

        Returns:
            Hashed password with salt
        """
        # Generate a random salt
        salt = os.urandom(32)

        # Hash password with salt using SHA-256
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # 100,000 iterations
        )

        # Store salt and hash together
        return salt.hex() + pwd_hash.hex()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            password_hash: Stored password hash

        Returns:
            True if password matches, False otherwise
        """
        try:
            # Extract salt (first 64 characters = 32 bytes in hex)
            salt = bytes.fromhex(password_hash[:64])
            stored_hash = password_hash[64:]

            # Hash the provided password with the same salt
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )

            # Compare hashes
            return pwd_hash.hex() == stored_hash
        except Exception:
            return False

    @classmethod
    def login(cls, username: str, password: str) -> tuple[bool, Optional[str]]:
        """
        Authenticate user and create session

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, error_message)
        """
        try:
            conn = DatabaseConnection.get_connection()

            # Normalize username (strip and lowercase for comparison)
            username_normalized = username.strip()

            # Get user from database (case-insensitive search)
            cursor = conn.execute("""
                SELECT user_id, username, password_hash, full_name, role, is_active
                FROM users
                WHERE LOWER(username) = LOWER(?)
            """, (username_normalized,))

            user = cursor.fetchone()

            if not user:
                print(f"Login failed: User '{username_normalized}' not found")
                return False, "Nom d'utilisateur ou mot de passe incorrect"

            if not user['is_active']:
                print(f"Login failed: User '{username_normalized}' is inactive")
                return False, "Ce compte est désactivé. Contactez l'administrateur."

            # Verify password
            if not cls.verify_password(password, user['password_hash']):
                print(f"Login failed: Invalid password for user '{username_normalized}'")
                return False, "Nom d'utilisateur ou mot de passe incorrect"

            # Update last login
            conn.execute("""
                UPDATE users
                SET last_login = ?
                WHERE user_id = ?
            """, (datetime.now().isoformat(), user['user_id']))
            conn.commit()

            # Create session
            cls.current_user = {
                'user_id': user['user_id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }

            print(f"Login successful for user '{user['username']}'")
            return True, None

        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Erreur de connexion: {str(e)}"

    @classmethod
    def logout(cls):
        """Clear current user session"""
        cls.current_user = None

    @classmethod
    def is_logged_in(cls) -> bool:
        """Check if a user is logged in"""
        return cls.current_user is not None

    @classmethod
    def is_admin(cls) -> bool:
        """Check if current user is admin"""
        return cls.current_user is not None and cls.current_user['role'] == 'admin'

    @classmethod
    def get_current_user(cls) -> Optional[Dict]:
        """Get current logged-in user"""
        return cls.current_user

    @classmethod
    def create_user(cls, username: str, password: str, full_name: str,
                   role: str = 'user') -> tuple[bool, Optional[str]]:
        """
        Create a new user (admin only)

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: 'admin' or 'user'

        Returns:
            Tuple of (success, error_message)
        """
        if not cls.is_admin():
            return False, "Seuls les administrateurs peuvent créer des utilisateurs"

        try:
            conn = DatabaseConnection.get_connection()

            # Normalize username (strip whitespace)
            username_normalized = username.strip()
            full_name_normalized = full_name.strip()

            # Check if username already exists (case-insensitive)
            cursor = conn.execute("SELECT username FROM users WHERE LOWER(username) = LOWER(?)", (username_normalized,))
            if cursor.fetchone():
                return False, "Ce nom d'utilisateur existe déjà"

            # Hash password
            password_hash = cls.hash_password(password)

            # Insert user
            cursor = conn.execute("""
                INSERT INTO users (username, password_hash, full_name, role, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (username_normalized, password_hash, full_name_normalized, role))
            conn.commit()

            # Get the new user ID
            new_user_id = cursor.lastrowid

            # Create default permissions
            cls.create_default_permissions(new_user_id, is_admin=(role == 'admin'))

            print(f"User '{username_normalized}' created successfully with ID {new_user_id}")
            return True, None

        except Exception as e:
            print(f"Error creating user: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Erreur lors de la création: {str(e)}"

    @classmethod
    def create_default_admin(cls) -> bool:
        """
        Create default admin account on first run
        Username: admin
        Password: admin

        Returns:
            True if created, False if already exists
        """
        try:
            conn = DatabaseConnection.get_connection()

            # Check if any users exist
            cursor = conn.execute("SELECT COUNT(*) as count FROM users")
            count = cursor.fetchone()['count']

            if count > 0:
                return False  # Users already exist

            # Create default admin
            password_hash = cls.hash_password("admin")

            cursor = conn.execute("""
                INSERT INTO users (username, password_hash, full_name, role, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, ("admin", password_hash, "Administrateur", "admin"))
            conn.commit()

            # Get the admin user ID
            admin_user_id = cursor.lastrowid

            # Create admin permissions
            cls.create_default_permissions(admin_user_id, is_admin=True)

            print("✓ Default admin account created (username: admin, password: admin)")
            print("⚠️  IMPORTANT: Change the default password after first login!")

            return True

        except Exception as e:
            print(f"Error creating default admin: {e}")
            return False

    @classmethod
    def change_password(cls, user_id: int, new_password: str) -> tuple[bool, Optional[str]]:
        """
        Change user password

        Args:
            user_id: User ID
            new_password: New plain text password

        Returns:
            Tuple of (success, error_message)
        """
        # Only admin or the user themselves can change password
        if not cls.is_admin() and (cls.current_user is None or cls.current_user['user_id'] != user_id):
            return False, "Permission refusée"

        try:
            conn = DatabaseConnection.get_connection()

            # Hash new password
            password_hash = cls.hash_password(new_password)

            # Update password
            conn.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE user_id = ?
            """, (password_hash, user_id))
            conn.commit()

            return True, None

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    @classmethod
    def toggle_user_active(cls, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Activate or deactivate a user (admin only)

        Args:
            user_id: User ID to toggle

        Returns:
            Tuple of (success, error_message)
        """
        if not cls.is_admin():
            return False, "Seuls les administrateurs peuvent désactiver des utilisateurs"

        try:
            conn = DatabaseConnection.get_connection()

            # Can't deactivate yourself
            if cls.current_user and cls.current_user['user_id'] == user_id:
                return False, "Vous ne pouvez pas désactiver votre propre compte"

            # Toggle active status
            conn.execute("""
                UPDATE users
                SET is_active = NOT is_active
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

            return True, None

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    @classmethod
    def delete_user(cls, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Delete a user (admin only)

        Args:
            user_id: User ID to delete

        Returns:
            Tuple of (success, error_message)
        """
        if not cls.is_admin():
            return False, "Seuls les administrateurs peuvent supprimer des utilisateurs"

        try:
            conn = DatabaseConnection.get_connection()

            # Can't delete yourself
            if cls.current_user and cls.current_user['user_id'] == user_id:
                return False, "Vous ne pouvez pas supprimer votre propre compte"

            # Delete user
            conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()

            return True, None

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    @classmethod
    def get_all_users(cls) -> list:
        """
        Get all users (admin only)

        Returns:
            List of user dictionaries
        """
        if not cls.is_admin():
            return []

        try:
            conn = DatabaseConnection.get_connection()

            cursor = conn.execute("""
                SELECT user_id, username, full_name, role, is_active, last_login, created_at
                FROM users
                ORDER BY created_at DESC
            """)

            return cursor.fetchall()

        except Exception:
            return []

    # ========================================================================
    # Permission Management Methods
    # ========================================================================

    @classmethod
    def get_user_permissions(cls, user_id: int = None) -> Optional[Dict]:
        """
        Get permissions for a user

        Args:
            user_id: User ID (defaults to current user)

        Returns:
            Dictionary of permissions or None
        """
        if user_id is None:
            if cls.current_user is None:
                return None
            user_id = cls.current_user['user_id']

        try:
            conn = DatabaseConnection.get_connection()

            cursor = conn.execute("""
                SELECT * FROM user_permissions
                WHERE user_id = ?
            """, (user_id,))

            return cursor.fetchone()

        except Exception:
            return None

    @classmethod
    def has_permission(cls, permission: str) -> bool:
        """
        Check if current user has a specific permission

        Args:
            permission: Permission name (e.g., 'can_edit_employees')

        Returns:
            True if user has permission, False otherwise
        """
        if not cls.is_logged_in():
            return False

        # Admins always have full access
        if cls.is_admin():
            return True

        permissions = cls.get_user_permissions()
        if not permissions:
            return False

        return permissions.get(permission, False) == 1

    @classmethod
    def set_user_permissions(cls, user_id: int, permissions: Dict) -> tuple[bool, Optional[str]]:
        """
        Set permissions for a user (admin only)

        Args:
            user_id: User ID
            permissions: Dictionary of permission flags

        Returns:
            Tuple of (success, error_message)
        """
        if not cls.is_admin():
            return False, "Seuls les administrateurs peuvent modifier les permissions"

        try:
            conn = DatabaseConnection.get_connection()

            # Check if permissions exist
            cursor = conn.execute("SELECT user_id FROM user_permissions WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing permissions
                set_clause = ", ".join([f"{key} = ?" for key in permissions.keys()])
                values = list(permissions.values()) + [user_id]
                conn.execute(f"""
                    UPDATE user_permissions
                    SET {set_clause}
                    WHERE user_id = ?
                """, values)
            else:
                # Insert new permissions
                columns = ", ".join(["user_id"] + list(permissions.keys()))
                placeholders = ", ".join(["?"] * (len(permissions) + 1))
                values = [user_id] + list(permissions.values())
                conn.execute(f"""
                    INSERT INTO user_permissions ({columns})
                    VALUES ({placeholders})
                """, values)

            conn.commit()
            return True, None

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    @classmethod
    def create_default_permissions(cls, user_id: int, is_admin: bool = False) -> bool:
        """
        Create default permissions for a new user

        Args:
            user_id: User ID
            is_admin: True for admin permissions, False for regular user

        Returns:
            True if successful
        """
        try:
            conn = DatabaseConnection.get_connection()

            if is_admin:
                # Admin gets full permissions
                conn.execute("""
                    INSERT INTO user_permissions (
                        user_id,
                        can_view_employees, can_edit_employees, can_delete_employees,
                        can_view_payroll, can_process_payroll, can_finalize_payroll,
                        can_view_loans, can_manage_loans,
                        can_generate_reports, can_export_data,
                        can_view_parameters, can_modify_parameters,
                        can_manage_users
                    ) VALUES (?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                """, (user_id,))
            else:
                # Regular user gets read-only permissions
                conn.execute("""
                    INSERT INTO user_permissions (
                        user_id,
                        can_view_employees, can_edit_employees, can_delete_employees,
                        can_view_payroll, can_process_payroll, can_finalize_payroll,
                        can_view_loans, can_manage_loans,
                        can_generate_reports, can_export_data,
                        can_view_parameters, can_modify_parameters,
                        can_manage_users
                    ) VALUES (?, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0)
                """, (user_id,))

            conn.commit()
            return True

        except Exception:
            return False
