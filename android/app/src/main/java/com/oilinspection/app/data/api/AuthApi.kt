package com.oilinspection.app.data.api

import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse
}
