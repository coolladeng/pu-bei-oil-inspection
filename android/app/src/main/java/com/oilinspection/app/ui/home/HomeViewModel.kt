package com.oilinspection.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.oilinspection.app.data.api.EquipmentItem
import com.oilinspection.app.data.api.HazardItem
import com.oilinspection.app.data.api.RunPlanItem
import com.oilinspection.app.data.api.UserProfile
import com.oilinspection.app.data.repository.AuthRepository
import com.oilinspection.app.data.api.InspectionApi
import com.oilinspection.app.data.repository.InspectionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val todayPlans: List<RunPlanItem> = emptyList(),
    val equipments: List<EquipmentItem> = emptyList(),
    val hazards: List<HazardItem> = emptyList(),
    val profile: UserProfile? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val completedCount: Int = 0,
    val totalCount: Int = 0,
    val equipTotal: Int = 0,
    val hazardTotal: Int = 0,
    val userName: String = "",
    val syncedCount: Int = 0
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val inspectionRepository: InspectionRepository,
    private val inspectionApi: InspectionApi,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadTodayPlans()
        syncPendingRecords()
    }

    fun loadTodayPlans() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val result = inspectionRepository.getTodayPlans()
            result.fold(
                onSuccess = { plans ->
                    val completed = plans.count { it.status == 1 }
                    _uiState.update {
                        it.copy(isLoading = false, todayPlans = plans,
                            totalCount = plans.size, completedCount = completed)
                    }
                },
                onFailure = { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message) }
                }
            )
        }
    }

    fun loadEquipments() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                val res = inspectionApi.getEquipments()
                _uiState.update { it.copy(isLoading = false, equipments = res.list, equipTotal = res.total) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, errorMessage = e.message) }
            }
        }
    }

    fun loadHazards() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            try {
                val res = inspectionApi.getHazards()
                _uiState.update { it.copy(isLoading = false, hazards = res.list, hazardTotal = res.total) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, errorMessage = e.message) }
            }
        }
    }

    fun loadProfile() {
        viewModelScope.launch {
            try {
                val profile = inspectionApi.getProfile()
                _uiState.update { it.copy(profile = profile, userName = profile.realName) }
            } catch (_: Exception) { }
        }
    }

    private fun syncPendingRecords() {
        viewModelScope.launch {
            val count = inspectionRepository.syncPendingRecords()
            if (count > 0) _uiState.update { it.copy(syncedCount = count) }
        }
    }

    fun logout() {
        viewModelScope.launch { authRepository.logout() }
    }
}
