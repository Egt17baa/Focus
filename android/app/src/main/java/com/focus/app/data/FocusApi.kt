package com.focus.app.data

import com.focus.app.BuildConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

class ApiException(message: String, val status: Int) : Exception(message)

/**
 * Thin OkHttp client for the Focus REST API. Access tokens are refreshed
 * transparently once per request when the API answers 401.
 */
class FocusApi(
    private val tokens: TokenStore,
    baseUrl: String = BuildConfig.API_BASE_URL,
) {
    private val base = baseUrl.trimEnd('/')
    private val json = Json { ignoreUnknownKeys = true }
    private val jsonType = "application/json; charset=utf-8".toMediaType()
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    suspend fun register(username: String, email: String, password: String): AuthResponse =
        authenticate("/auth/register", buildJson("username" to username, "email" to email, "password" to password))

    suspend fun login(identifier: String, password: String): AuthResponse =
        authenticate("/auth/login", buildJson("username" to identifier, "password" to password))

    suspend fun logout() {
        runCatching { request("POST", "/auth/logout", empty(), authenticated = true) }
        tokens.clear()
    }

    suspend fun me(): User = decode(request("GET", "/users/me", null, authenticated = true))

    suspend fun updateProfile(dailyGoalMinutes: Int? = null, avatarEmoji: String? = null): User {
        val fields = buildMap {
            dailyGoalMinutes?.let { put("daily_goal_minutes", it.toString()) }
            avatarEmoji?.let { put("avatar_emoji", "\"$it\"") }
        }
        val body = fields.entries.joinToString(",", "{", "}") { "\"${it.key}\":${it.value}" }
        return decode(request("PATCH", "/users/me", body.toRequestBody(jsonType), authenticated = true))
    }

    suspend fun activeSession(): FocusSession? =
        decode<ActiveSessionResponse>(request("GET", "/sessions/active", null, authenticated = true)).session

    suspend fun startSession(mode: String, plannedMinutes: Int, tag: String?): FocusSession {
        val tagJson = tag?.takeIf { it.isNotBlank() }?.let { "\"$it\"" } ?: "null"
        val body = """{"mode":"$mode","planned_minutes":$plannedMinutes,"tag":$tagJson,"source":"android"}"""
        return decode(request("POST", "/sessions", body.toRequestBody(jsonType), authenticated = true))
    }

    suspend fun pause(id: Int): FocusSession =
        decode(request("POST", "/sessions/$id/pause", empty(), authenticated = true))

    suspend fun resume(id: Int): FocusSession =
        decode(request("POST", "/sessions/$id/resume", empty(), authenticated = true))

    suspend fun complete(id: Int): CompleteSessionResponse =
        decode(request("POST", "/sessions/$id/complete", empty(), authenticated = true))

    suspend fun abandon(id: Int): FocusSession =
        decode(request("POST", "/sessions/$id/abandon", empty(), authenticated = true))

    suspend fun stats(days: Int = 30): StatsResponse =
        decode(request("GET", "/stats/overview?days=$days", null, authenticated = true))

    suspend fun achievements(): List<EarnedAchievement> =
        json.decodeFromString<Map<String, List<EarnedAchievement>>>(
            request("GET", "/stats/achievements", null, authenticated = true),
        )["earned"].orEmpty()

    suspend fun blockedApps(): List<BlockedApp> =
        decode<BlockedAppsResponse>(request("GET", "/blocked-apps", null, authenticated = true)).apps

    suspend fun addBlockedApp(appName: String, packageName: String?): BlockedApp {
        val pkg = packageName?.takeIf { it.isNotBlank() }?.let { "\"$it\"" } ?: "null"
        val body = """{"app_name":"$appName","package_name":$pkg}"""
        return decode(request("POST", "/blocked-apps", body.toRequestBody(jsonType), authenticated = true))
    }

    suspend fun deleteBlockedApp(id: Int) {
        request("DELETE", "/blocked-apps/$id", null, authenticated = true)
    }

    suspend fun shouldBlock(packageName: String): BlockCheckResponse = decode(
        request(
            "POST",
            "/blocked-apps/check",
            """{"package_name":"$packageName"}""".toRequestBody(jsonType),
            authenticated = true,
        ),
    )

    private suspend fun authenticate(path: String, body: RequestBody): AuthResponse {
        val response = decode<AuthResponse>(request("POST", path, body, authenticated = false))
        tokens.save(response.accessToken, response.refreshToken)
        return response
    }

    private fun buildJson(vararg pairs: Pair<String, String>): RequestBody =
        pairs.joinToString(",", "{", "}") { "\"${it.first}\":\"${it.second}\"" }.toRequestBody(jsonType)

    private fun empty(): RequestBody = "{}".toRequestBody(jsonType)

    private inline fun <reified T> decode(body: String): T = json.decodeFromString(body)

    private suspend fun request(
        method: String,
        path: String,
        body: RequestBody?,
        authenticated: Boolean,
        retryOnUnauthorized: Boolean = true,
    ): String = withContext(Dispatchers.IO) {
        val builder = Request.Builder().url("$base$path").method(method, body)
        if (authenticated) {
            tokens.access()?.let { builder.header("Authorization", "Bearer $it") }
        }
        client.newCall(builder.build()).execute().use { response ->
            val text = response.body?.string().orEmpty()
            when {
                response.isSuccessful -> text
                response.code == 401 && authenticated && retryOnUnauthorized && renewAccessToken() ->
                    request(method, path, body, authenticated, retryOnUnauthorized = false)
                else -> throw ApiException(errorMessage(text, response.code), response.code)
            }
        }
    }

    private fun errorMessage(body: String, status: Int): String =
        runCatching { json.decodeFromString<ApiMessage>(body).error }.getOrNull()
            ?: "Error de red ($status)"

    private suspend fun renewAccessToken(): Boolean {
        val refreshToken = tokens.refresh() ?: return false
        val request = Request.Builder()
            .url("$base/auth/refresh")
            .post(empty())
            .header("Authorization", "Bearer $refreshToken")
            .build()
        return withContext(Dispatchers.IO) {
            client.newCall(request).execute().use { response ->
                val text = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    tokens.clear()
                    false
                } else {
                    tokens.saveAccess(json.decodeFromString<RefreshResponse>(text).accessToken)
                    true
                }
            }
        }
    }
}
