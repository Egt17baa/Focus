package com.focus.app.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: Int,
    val username: String,
    val email: String,
    @SerialName("total_focus_points") val totalFocusPoints: Int = 0,
    val level: Int = 1,
    @SerialName("level_name") val levelName: String = "Novato",
    @SerialName("level_progress") val levelProgress: Double = 0.0,
    @SerialName("points_to_next_level") val pointsToNextLevel: Int = 0,
    @SerialName("daily_goal_minutes") val dailyGoalMinutes: Int = 120,
    @SerialName("avatar_emoji") val avatarEmoji: String = "\uD83C\uDFAF",
)

@Serializable
data class AuthResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    val user: User,
)

@Serializable
data class RefreshResponse(@SerialName("access_token") val accessToken: String)

@Serializable
data class FocusSession(
    val id: Int,
    val mode: String,
    val status: String,
    val tag: String? = null,
    val source: String = "android",
    @SerialName("planned_minutes") val plannedMinutes: Int,
    @SerialName("focus_minutes") val focusMinutes: Int = 0,
    val interruptions: Int = 0,
    @SerialName("points_earned") val pointsEarned: Int = 0,
    @SerialName("elapsed_seconds") val elapsedSeconds: Int = 0,
) {
    val plannedSeconds: Int get() = plannedMinutes * 60

    val isRunning: Boolean get() = status == "running"

    val isPaused: Boolean get() = status == "paused"
}

@Serializable
data class ActiveSessionResponse(val session: FocusSession? = null)

@Serializable
data class Achievement(
    val key: String = "",
    val name: String = "",
    val description: String = "",
    val icon: String = "\u2B50",
    val points: Int = 0,
)

@Serializable
data class EarnedAchievement(
    val id: Int = 0,
    val achievement: Achievement = Achievement(),
    @SerialName("earned_at") val earnedAt: String? = null,
)

@Serializable
data class CompleteSessionResponse(
    val session: FocusSession,
    val user: User,
    @SerialName("unlocked_achievements") val unlockedAchievements: List<EarnedAchievement> = emptyList(),
)

@Serializable
data class Overview(
    @SerialName("total_sessions") val totalSessions: Int = 0,
    @SerialName("total_minutes") val totalMinutes: Int = 0,
    @SerialName("average_minutes") val averageMinutes: Double = 0.0,
    @SerialName("today_minutes") val todayMinutes: Int = 0,
    @SerialName("week_minutes") val weekMinutes: Int = 0,
    @SerialName("daily_goal_minutes") val dailyGoalMinutes: Int = 0,
    @SerialName("daily_goal_progress") val dailyGoalProgress: Double = 0.0,
    @SerialName("completion_rate") val completionRate: Double = 0.0,
    @SerialName("current_streak") val currentStreak: Int = 0,
    @SerialName("longest_streak") val longestStreak: Int = 0,
    @SerialName("total_points") val totalPoints: Int = 0,
    @SerialName("level_name") val levelName: String = "Novato",
    @SerialName("level_progress") val levelProgress: Double = 0.0,
)

@Serializable
data class DailyPoint(val date: String, val minutes: Int = 0, val sessions: Int = 0)

@Serializable
data class TagPoint(val tag: String, val minutes: Int = 0, val sessions: Int = 0)

@Serializable
data class StatsResponse(
    val overview: Overview = Overview(),
    val daily: List<DailyPoint> = emptyList(),
    val tags: List<TagPoint> = emptyList(),
)

@Serializable
data class BlockedApp(
    val id: Int,
    @SerialName("app_name") val appName: String,
    @SerialName("package_name") val packageName: String? = null,
    val category: String = "otras",
    @SerialName("is_active") val isActive: Boolean = true,
)

@Serializable
data class BlockedAppsResponse(val apps: List<BlockedApp> = emptyList())

@Serializable
data class BlockCheckResponse(
    @SerialName("should_block") val shouldBlock: Boolean = false,
    val reason: String? = null,
)

@Serializable
data class ApiMessage(val error: String? = null, val message: String? = null)
