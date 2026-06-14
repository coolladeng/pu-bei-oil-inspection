package com.oilinspection.app.data.repository

import com.oilinspection.app.data.api.AuthApi
import com.oilinspection.app.data.api.LoginRequest
import com.oilinspection.app.data.api.LoginResponse
import com.oilinspection.app.data.local.TokenManager
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager
) {

    suspend fun login(username: String, password: String): Result<LoginResponse> {
        return try {
            val response = authApi.login(LoginRequest(username, password))
            tokenManager.saveLoginInfo(
                token = response.accessToken,
                username = response.user.username,
                realName = response.user.realName,
                role = response.user.roles?.firstOrNull() ?: ""
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(Exception("连接服务器失败: " + e.message))
        }
    }

    suspend fun isLoggedIn(): Boolean {
        return !tokenManager.getToken().isNullOrEmpty()
    }

    suspend fun logout() {
        tokenManager.clear()
    }
}
