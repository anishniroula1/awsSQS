# Adjusting for a simplified approach to ensure all sections are included without encoding issues.
from fpdf import FPDF
class SimplifiedPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'App Development User Stories Complete', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = SimplifiedPDF()
pdf.add_page()

# Full content with all sections for the complete PDF
full_content = {
    "Account Management": """1. User Registration: As a new user, I want to register for an account using my email address, so that I can securely use the app.
2. User Login: As an existing user, I want to log in to my account with my email and password, so that I can access my messages and chats.
3. Account Recovery: As a user who has forgotten my password, I want to be able to reset my password securely, so that I can regain access to my account.
4. Account Details Recovery: As a user who has forgotten my account details, I want to recover my account using my email, so that I can continue using the app without losing my data.
5. Logout: As a user, I want to log out of my account from the app, so that I can ensure my account is secure when I'm not using it.""",

    "Chat Management": """1. Start New Chat: As a user, I want to start a new chat with another user by searching for their username or email, so that I can communicate privately.
2. Set Chat Password: As a user starting a new chat, I want to set a unique password for the chat, so that the conversation remains secure and private.
3. Receive Chat Invitation: As a user, I want to receive notifications for chat invitations, so I can accept or decline them based on my willingness to engage.
4. View Chats: As a user, I want to view a list of my active chats, so I can easily select and continue conversations.
5. Manage Chat Settings: As a user, I want to manage settings for individual chats, such as notifications and participants, to customize my chat experience.
6. Leave or Delete Chat: As a user, I want the option to leave or delete a chat, so that I can manage my conversations and maintain privacy.
7. Chat Backup and Recovery: As a user, I want to back up my chats and recover them if needed, so that I don't lose important conversations.""",

    "Messaging": """1. Send Message: As a user, I want to send text messages to a chat, so that I can communicate with the other participant(s).
2. Receive Message: As a user, I want to receive messages in real-time, so that I can promptly respond to conversations.
3. Message Notifications: As a user, I want to receive notifications for new messages, so that I don’t miss important communications.
4. Send Media: As a user, I want to send images and videos within chats, so that I can share more than just text.
5. Message Formatting: As a user, I want to format my messages, so that I can emphasize certain words or phrases.
6. Search Within Conversations: As a user, I want to search for specific messages within a chat, so that I can quickly find important information.
7. Delete Messages: As a user, I want to delete messages from a chat, so that I can remove content I no longer want shared.
8. Self-Destructing Messages: As a user, I want to send messages that self-destruct after being read, so that I can ensure sensitive information is not permanently stored.""",

    "Security & Privacy": """1. End-to-End Encryption Setup: As a user, I want my messages to be end-to-end encrypted, so only the intended recipient(s) and I can read them.
2. Enter Chat Password: As a user, I want to enter a password to access secure chats, ensuring that conversations remain private even if my device is compromised.
3. Password Reset Request: As a user, I want to securely request a password reset for a chat if I forget it, ensuring I can regain access without compromising security.
4. Approve Password Reset: As a chat participant, I want to approve or deny password reset requests, so I can ensure the security of our conversation.
5. Use Secret PIN for Password Reset: As a user, I want to use a secret PIN to reset a chat password if my chat partner is unavailable to approve the reset, ensuring access is maintained without compromising security.""",

    "App Settings and Support": """1. Change User Settings: As a user, I want to change my account settings, including my profile information and security preferences, so that I can customize my app experience according to my needs.
2. Manage Notification Preferences: As a user, I want to manage my notification preferences, so that I can control how and when I get alerts from the app.
3. Help and Support Access: As a user, I want easy access to help and support resources, so that I can find answers to my questions or resolve issues quickly.
4. Report Bugs and Feedback: As a user, I want to report bugs and submit feedback directly through the app, so that I can contribute to its improvement and reliability.
5. Data and Privacy Management: As a user, I want to review and manage my data and privacy settings, so that I have control over my personal information and its use within the app.
6. Language and Accessibility Options: As a user, I want to select my preferred language and configure accessibility options, so that the app is inclusive and easy to use.
7. Logout and Account Deactivation: As a user, I want the option to log out or deactivate my account, so that I can take breaks or permanently leave the platform if I choose to.""",

    "Data Management and Performance": """1. Sync Messages Across Devices: As a user, I want my messages and chats to sync across all my devices, so I can switch between them seamlessly without losing any information.
2. Optimize Data Usage: As a user, I want the app to optimize its data usage, especially on mobile networks, so that I don’t consume too much of my data plan.
3. Manage Storage: As a user, I want to manage the app’s storage on my device, so I can free up space when needed without losing important information.
4. Backup and Restore Conversations: As a user, I want to backup my conversations and be able to restore them, so that I can safeguard against data loss.
5. Efficient Message Loading and Scrolling: As a user, I want the app to load messages quickly and allow for smooth scrolling, so that I can navigate my conversations without lag or delay.
6. Energy Efficient Operation: As a user, I want the app to operate efficiently in terms of energy consumption, so that it doesn’t drain my device’s battery quickly.
7. Handling Large Media Files: As a user, I want the app to handle large media files efficiently, so that I can share high-quality images and videos without issues."""
}

# Generating the complete PDF with all sections
pdf = FPDF()
pdf.add_page()

for title, story in full_content.items():
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='L')
    pdf.set_font("Arial", size=10)
    story = story.replace('\n', '\n\n')  # Add extra space for readability
    pdf.multi_cell(0, 10, txt=story)
    pdf.ln(10)  # Add some space before the next section

# Save the complete PDF to a file
complete_pdf_path = "/mnt/data/Complete_App_Development_User_Stories.pdf"
pdf.output(complete_pdf_path)
