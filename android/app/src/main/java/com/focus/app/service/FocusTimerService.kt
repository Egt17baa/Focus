package com.focus.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.focus.app.MainActivity
import com.focus.app.R
import com.focus.app.data.formatClock
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Keeps the focus countdown alive (and visible) while the app is in background.
 */
class FocusTimerService : Service() {
    private val scope = CoroutineScope(Dispatchers.Default)
    private var ticker: Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val remaining = intent?.getIntExtra(EXTRA_REMAINING_SECONDS, 0) ?: 0
        createChannel()
        startForeground(NOTIFICATION_ID, buildNotification(remaining))
        ticker?.cancel()
        ticker = scope.launch {
            var left = remaining
            while (left > 0) {
                delay(1000)
                left -= 1
                notificationManager().notify(NOTIFICATION_ID, buildNotification(left))
            }
            notificationManager().notify(NOTIFICATION_ID, buildNotification(0, finished = true))
        }
        return START_STICKY
    }

    override fun onDestroy() {
        ticker?.cancel()
        scope.cancel()
        super.onDestroy()
    }

    private fun notificationManager(): NotificationManager =
        getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    private fun createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val channel = NotificationChannel(
            CHANNEL_ID,
            getString(R.string.timer_channel_name),
            NotificationManager.IMPORTANCE_LOW,
        )
        channel.setShowBadge(false)
        notificationManager().createNotificationChannel(channel)
    }

    private fun buildNotification(remainingSeconds: Int, finished: Boolean = false): Notification {
        val intent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        val text = if (finished) {
            getString(R.string.timer_finished)
        } else {
            getString(R.string.timer_remaining, formatClock(remainingSeconds))
        }
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_focus_notification)
            .setContentTitle(getString(R.string.timer_title))
            .setContentText(text)
            .setOngoing(!finished)
            .setSilent(!finished)
            .setContentIntent(intent)
            .build()
    }

    companion object {
        private const val CHANNEL_ID = "focus_timer"
        private const val NOTIFICATION_ID = 1001
        private const val EXTRA_REMAINING_SECONDS = "remaining_seconds"

        fun start(context: Context, remainingSeconds: Int) {
            val intent = Intent(context, FocusTimerService::class.java)
                .putExtra(EXTRA_REMAINING_SECONDS, remainingSeconds.coerceAtLeast(0))
            context.startForegroundService(intent)
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, FocusTimerService::class.java))
        }
    }
}
