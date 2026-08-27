package com.focus.app.data

/** Formats a countdown as mm:ss (or h:mm:ss for sessions over one hour). */
fun formatClock(totalSeconds: Int): String {
    val seconds = totalSeconds.coerceAtLeast(0)
    val hours = seconds / 3600
    val minutes = (seconds % 3600) / 60
    val rest = seconds % 60
    return if (hours > 0) {
        "%d:%02d:%02d".format(hours, minutes, rest)
    } else {
        "%02d:%02d".format(minutes, rest)
    }
}

/** Progress in [0f, 1f] of a session given the elapsed and planned seconds. */
fun sessionProgress(elapsedSeconds: Int, plannedSeconds: Int): Float {
    if (plannedSeconds <= 0) return 0f
    return (elapsedSeconds.toFloat() / plannedSeconds).coerceIn(0f, 1f)
}
