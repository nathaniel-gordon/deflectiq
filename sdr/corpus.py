"""Demo knowledge base for 'CloudDrive' (file-sync SaaS): KB articles + resolved tickets."""
from __future__ import annotations

KB_ARTICLES = {
    "kb-sync-conflicts": ("Resolving sync conflicts",
        "When the same file is edited on two devices before syncing, CloudDrive keeps both "
        "versions and names the newer one 'filename (conflicted copy YYYY-MM-DD)'. To resolve, "
        "open both versions, merge changes manually, delete the conflicted copy, and let sync "
        "complete. Enable 'notify on conflict' in Settings > Sync to catch conflicts early."),
    "kb-selective-sync": ("Using selective sync to save disk space",
        "Selective sync lets you choose which folders download to each device. Go to Settings > "
        "Sync > Selective Sync, untick folders to keep them cloud-only. Files remain visible in "
        "the web app. Unticking a folder removes its local copy but never deletes cloud data."),
    "kb-restore-deleted": ("Restoring deleted files and versions",
        "Deleted files stay in the Trash for 30 days on Free and 180 days on Business plans. "
        "Open the web app, go to Trash, select files, click Restore. For older versions of an "
        "existing file, right-click the file, choose Version history, and restore any version "
        "from the last 30 or 180 days depending on plan."),
    "kb-bandwidth-limits": ("Configuring upload and download bandwidth limits",
        "To stop CloudDrive saturating your network, open Settings > Network and set upload and "
        "download rate limits in KB/s, or choose 'auto' which caps uploads at 75 percent of "
        "available bandwidth. On corporate networks an administrator can enforce limits via the "
        "policy console."),
    "kb-shared-link-permissions": ("Shared link permissions and passwords",
        "Shared links can be view-only or allow downloads. Business plans can add link "
        "passwords and expiry dates: create a link, click the gear icon, set 'require password' "
        "and 'expires after'. Editors on a shared folder need accounts; link recipients do not."),
    "kb-storage-full": ("What happens when storage is full",
        "When your quota is exhausted, syncing pauses and new uploads fail with 'storage full'. "
        "Existing files stay accessible. Free space by emptying Trash (it counts toward quota), "
        "removing large files, or upgrading your plan. Sync resumes automatically within five "
        "minutes of space becoming available."),
    "kb-two-factor": ("Enabling two-factor authentication",
        "Enable 2FA under Account > Security. CloudDrive supports authenticator apps and "
        "hardware keys; SMS is not offered. Save the recovery codes shown at setup. Lost "
        "authenticator devices require a recovery code or a support identity check taking up "
        "to two business days."),
    "kb-team-roles": ("Team roles and admin permissions",
        "Business workspaces have three roles: member, admin, and owner. Admins manage users, "
        "shared folders, and policies; only the owner can change billing or delete the "
        "workspace. Assign roles under Admin Console > Members. Role changes apply within a "
        "minute and are logged in the audit trail."),
    "kb-camera-upload": ("Troubleshooting mobile camera upload",
        "If camera upload stalls: check the app has photo permissions, disable battery "
        "optimization for CloudDrive, and ensure 'upload on cellular' matches your intent. "
        "Uploads pause below 20 percent battery by design. HEIC photos convert to JPEG when "
        "'compatibility mode' is on."),
    "kb-linux-client": ("Installing the Linux client",
        "The Linux client ships as a deb and rpm package plus a headless CLI. Install the "
        "package, run clouddrive login, and a browser window completes authentication. For "
        "servers, use clouddrive login --no-browser to get a pairing code. The daemon syncs "
        "under ~/CloudDrive by default; change with clouddrive config set sync-root."),
}

RESOLVED_TICKETS = {
    "rt-1042": ("conflicted copy files everywhere after laptop came back online",
        "Explained conflicted-copy naming; user merged changes and enabled conflict "
        "notifications. Root cause: offline edits on two devices.", "kb-sync-conflicts"),
    "rt-1187": ("out of space but I deleted lots of files yesterday",
        "Trash still counted toward quota. User emptied Trash, sync resumed automatically.",
        "kb-storage-full"),
    "rt-1201": ("shared a folder but client cannot edit files",
        "Recipient used a view-only link. Created editor invite to the folder instead; "
        "explained link vs folder permissions.", "kb-shared-link-permissions"),
    "rt-1244": ("need old version of a spreadsheet from last month",
        "Business plan retains 180 days of versions; walked through Version history restore.",
        "kb-restore-deleted"),
    "rt-1290": ("cloud drive is eating all our office bandwidth during backups",
        "Set upload limit to 2000 KB/s via policy console for the office network.",
        "kb-bandwidth-limits"),
    "rt-1333": ("photos from phone stopped backing up since android update",
        "Photo permission was revoked by the OS update; re-granted and disabled battery "
        "optimization. Uploads resumed.", "kb-camera-upload"),
    "rt-1360": ("lost my phone with the authenticator app cannot log in",
        "User had no recovery codes; completed identity verification, 2FA reset after review.",
        "kb-two-factor"),
    "rt-1402": ("want some folders cloud only on my small ssd laptop",
        "Configured selective sync; explained cloud-only behavior.", "kb-selective-sync"),
    "rt-1447": ("make a colleague admin so she can add users",
        "Owner promoted colleague to admin in Admin Console > Members.", "kb-team-roles"),
    "rt-1503": ("install on ubuntu server without a desktop browser",
        "Used clouddrive login --no-browser pairing-code flow on the headless server.",
        "kb-linux-client"),
}

# incoming test tickets: (text, expected_article or None if human-needed)
TEST_TICKETS = [
    ("my files say conflicted copy with a date in the name, which one is real", "kb-sync-conflicts"),
    ("getting storage full errors even though i emptied a bunch of stuff", "kb-storage-full"),
    ("how do i limit the sync speed so zoom calls stop lagging", "kb-bandwidth-limits"),
    ("can i password protect a link i send to an external client", "kb-shared-link-permissions"),
    ("recover a file my coworker deleted two weeks ago", "kb-restore-deleted"),
    ("phone photos not uploading anymore after the ios update", "kb-camera-upload"),
    ("set up cloudDrive on a headless debian box", "kb-linux-client"),
    ("i want to stop syncing the videos folder to this laptop", "kb-selective-sync"),
    ("please merge my two accounts and transfer ownership of all shared folders "
     "while keeping the billing history from the older one", None),
    ("your app corrupted my tax documents and i want compensation", None),
]
