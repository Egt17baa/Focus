package com.focus.app.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.focus.app.data.ApiException
import com.focus.app.data.BlockedApp
import com.focus.app.data.EarnedAchievement
import com.focus.app.data.FocusApi
import com.focus.app.data.FocusSession
import com.focus.app.data.StatsResponse
import com.focus.app.data.TokenStore
import com.focus.app.data.User
import com.focus.app.service.FocusTimerService
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class FocusUiState(
    val loading: Boolean = true,
    val user: User? = null,
    val session: FocusSession? = null,
    val elapsedSeconds: Int = 0,
    val stats: StatsResponse? = null,
    val achievements: List<EarnedAchievement> = emptyList(),
    val blockedApps: List<BlockedApp> = emptyList(),
    val error: String? = null,
    val justUnlocked: List<EarnedAchievement> = emptyList(),
) {
    val isAuthenticated: Boolean get() = user != null
}

class FocusViewModel(application: Application) : AndroidViewModel(application) {
    private val tokens = TokenStore(application)
    private val api = FocusApi(tokens)
    private val _state = MutableStateFlow(FocusUiState())
    val state: StateFlow<FocusUiState> = _state.asStateFlow()
    private var ticker: Job? = null

    init {
        viewModelScope.launch {
            if (tokens.access() == null) {
                _state.update { it.copy(loading = false) }
            } else {
                runSafely { loadEverything() }
                _state.update { it.copy(loading = false) }
            }
        }
    }

    fun login(identifier: String, password: String) = launchAuth {
        api.login(identifier.trim(), password)
    }

    fun register(username: String, email: String, password: String) = launchAuth {
        api.register(username.trim(), email.trim(), password)
    }

    fun logout() {
        stopTicker()
        viewModelScope.launch {
            api.logout()
            FocusTimerService.stop(getApplication())
            _state.value = FocusUiState(loading = false)
        }
    }

    fun start(mode: String, minutes: Int, tag: String?) = viewModelScope.launch {
        runSafely {
            applySession(api.startSession(mode, minutes, tag))
            refreshStats()
        }
    }

    fun pause() = withSession { session ->
        applySession(api.pause(session.id))
    }

    fun resume() = withSession { session ->
        applySession(api.resume(session.id))
    }

    fun complete() = withSession { session ->
        val result = api.complete(session.id)
        applySession(null)
        _state.update {
            it.copy(user = result.user, justUnlocked = result.unlockedAchievements)
        }
        refreshStats()
        loadAchievements()
    }

    fun abandon() = withSession { session ->
        api.abandon(session.id)
        applySession(null)
        refreshStats()
    }

    fun addBlockedApp(name: String, packageName: String?) = viewModelScope.launch {
        runSafely {
            api.addBlockedApp(name.trim(), packageName?.trim())
            _state.update { it.copy(blockedApps = api.blockedApps()) }
        }
    }

    fun removeBlockedApp(id: Int) = viewModelScope.launch {
        runSafely {
            api.deleteBlockedApp(id)
            _state.update { it.copy(blockedApps = api.blockedApps()) }
        }
    }

    fun updateDailyGoal(minutes: Int) = viewModelScope.launch {
        runSafely {
            val user = api.updateProfile(dailyGoalMinutes = minutes)
            _state.update { it.copy(user = user) }
            refreshStats()
        }
    }

    fun refresh() = viewModelScope.launch { runSafely { loadEverything() } }

    fun dismissError() = _state.update { it.copy(error = null) }

    fun dismissUnlocked() = _state.update { it.copy(justUnlocked = emptyList()) }

    private fun launchAuth(block: suspend () -> Unit) = viewModelScope.launch {
        _state.update { it.copy(loading = true, error = null) }
        runSafely {
            block()
            loadEverything()
        }
        _state.update { it.copy(loading = false) }
    }

    private fun withSession(block: suspend (FocusSession) -> Unit) = viewModelScope.launch {
        val session = _state.value.session ?: return@launch
        runSafely { block(session) }
    }

    private suspend fun loadEverything() {
        _state.update { it.copy(user = api.me()) }
        applySession(api.activeSession())
        refreshStats()
        loadAchievements()
        _state.update { it.copy(blockedApps = api.blockedApps()) }
    }

    private suspend fun refreshStats() {
        _state.update { it.copy(stats = api.stats()) }
    }

    private suspend fun loadAchievements() {
        _state.update { it.copy(achievements = api.achievements()) }
    }

    private fun applySession(session: FocusSession?) {
        _state.update { it.copy(session = session, elapsedSeconds = session?.elapsedSeconds ?: 0) }
        val context = getApplication<Application>()
        if (session != null && session.isRunning) {
            FocusTimerService.start(context, session.plannedSeconds - session.elapsedSeconds)
            startTicker()
        } else {
            stopTicker()
            if (session == null || !session.isPaused) FocusTimerService.stop(context)
        }
    }

    private fun startTicker() {
        stopTicker()
        ticker = viewModelScope.launch {
            while (true) {
                delay(1000)
                _state.update { it.copy(elapsedSeconds = it.elapsedSeconds + 1) }
            }
        }
    }

    private fun stopTicker() {
        ticker?.cancel()
        ticker = null
    }

    private suspend fun runSafely(block: suspend () -> Unit) {
        try {
            block()
        } catch (exception: ApiException) {
            if (exception.status == 401) {
                _state.value = FocusUiState(loading = false, error = "Tu sesión ha caducado")
            } else {
                _state.update { it.copy(error = exception.message) }
            }
        } catch (exception: Exception) {
            _state.update { it.copy(error = exception.message ?: "Error inesperado") }
        }
    }

    override fun onCleared() {
        stopTicker()
        super.onCleared()
    }

    companion object {
        val Factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(
                modelClass: Class<T>,
                extras: androidx.lifecycle.viewmodel.CreationExtras,
            ): T {
                val application = extras[ViewModelProvider.AndroidViewModelFactory.APPLICATION_KEY]!!
                return FocusViewModel(application) as T
            }
        }
    }
}
