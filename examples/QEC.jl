# Dependency-free binary algebra and exact small-code decoding for the textbook.
module QEC
export gf2rank, gf2solve, hgp, steane_H, syndrome, pure_error, joint_weights,
       exact_failure, repetition_failure, verify

function rref2(A)
    B = Int.(A) .% 2
    row = 1; pivots = Int[]
    for col in axes(B, 2)
        row > size(B, 1) && break
        pivot = findfirst(i -> B[i, col] == 1, row:size(B, 1))
        isnothing(pivot) && continue
        p = row + pivot - 1
        B[row, :], B[p, :] = copy(B[p, :]), copy(B[row, :])
        for i in axes(B, 1)
            if i != row && B[i, col] == 1
                B[i, :] .= xor.(B[i, :], B[row, :])
            end
        end
        push!(pivots, col); row += 1
    end
    B, pivots
end
gf2rank(A) = length(last(rref2(A)))

"""Solve H*x=s over GF(2), fixing free variables to zero; reject inconsistent s."""
function gf2solve(H, s)
    size(H, 1) == length(s) || throw(DimensionMismatch())
    B, piv = rref2(hcat(H, s))
    n = size(H, 2)
    n + 1 in piv && throw(ArgumentError("inconsistent binary system"))
    x = zeros(Int, n)
    for (row, col) in enumerate(piv)
        x[col] = B[row, end]
    end
    @assert mod.(H*x, 2) == mod.(s, 2)
    x
end

function hgp(H1, H2)
    m1, n1 = size(H1); m2, n2 = size(H2)
    eye(n) = Matrix{Int}(I, n, n)
    HX = hcat(kron(H1, eye(n2)), kron(eye(m1), transpose(H2)))
    HZ = hcat(kron(eye(n1), H2), kron(transpose(H1), eye(m2)))
    HX, HZ
end
using LinearAlgebra: I

"""Columns are the nonzero 3-bit vectors, least significant bit first."""
steane_H() = [Int((j >> i) & 1) for i in 0:2, j in 1:7]
syndrome(e::Integer) = foldl(xor, (j for j in 1:7 if ((e >> (j-1)) & 1) == 1); init=0)
pure_error(s::Integer) = s == 0 ? 0 : 1 << (s-1)

"""P(s,logical residual parity), X-only Steane noise: iid + a fixed pair burst."""
function joint_weights(p::Real, alpha::Real=0.0)
    0 <= p <= 1 || throw(ArgumentError("p outside [0,1]"))
    0 <= alpha <= 1 || throw(ArgumentError("alpha outside [0,1]"))
    W = zeros(8,2)
    for e in 0:127
        w = count_ones(e)
        prob = (1-alpha)*p^w*(1-p)^(7-w) + (e == 3 ? alpha : 0)
        s = syndrome(e)
        ell = count_ones(xor(e,pure_error(s))) % 2
        W[s+1,ell+1] += prob
    end
    @assert isapprox(sum(W), 1; atol=1e-12)
    W
end
exact_failure(W) = sum(min(W[s,1],W[s,2]) for s in axes(W,1))
function repetition_failure(d::Integer,p::Real)
    d > 0 && isodd(d) || throw(ArgumentError("distance must be positive and odd"))
    0 <= p <= 1 || throw(ArgumentError("p outside [0,1]"))
    sum(binomial(big(d),w)*big(p)^w*(1-big(p))^(d-w) for w in (d+1)÷2:d)
end

function verify()
    H = steane_H()
    @assert gf2rank(H)==3 && all(iszero, mod.(H*H',2))
    for s in 0:7
        bits = [(s >> i)&1 for i in 0:2]
        @assert mod.(H*gf2solve(H,bits),2)==bits
        @assert syndrome(pure_error(s))==s
    end
    # Kernel classes equal the stabilizer span and its odd-weight coset.
    span = Set(foldl(xor, (sum(H[i,j] << (j-1) for j in 1:7)
                   for i in 1:3 if ((u>>(i-1))&1)==1); init=0) for u in 0:7)
    @assert length(span)==8
    for e in 0:127
        r=xor(e,pure_error(syndrome(e)))
        @assert (r in span) == iseven(count_ones(r))
    end
    HX,HZ=hgp([1 1],[1 1])
    @assert all(iszero,mod.(HX*HZ',2))
    @assert size(HX,2)-gf2rank(HX)-gf2rank(HZ)==1
    # Detect an inconsistent dependent check system.
    rejected=false
    try gf2solve([1 1;1 1],[0,1]) catch e
        e isa ArgumentError || rethrow(); rejected=true
    end
    @assert rejected
    println("All binary-algebra and 128-error logical-class checks passed.")
end
end
