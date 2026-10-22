include("QEC.jl")
using .QEC
QEC.verify()
out = joinpath(@__DIR__, "..", "data", "exact-decoding.csv")
open(out,"w") do io
    println(io,"p,alpha,minimum_weight_failure,exact_ml_failure")
    for alpha in (0.0,0.08,0.18), p in (0.01,0.03,0.06,0.1,0.2)
        W=joint_weights(p,alpha)
        println(io,join((p,alpha,sum(W[:,2]),exact_failure(W)),','))
    end
end
for (p,alpha) in ((0.06,0.0),(0.06,0.18))
    W=joint_weights(p,alpha)
    println("p=$p alpha=$alpha: minimum-weight=$(sum(W[:,2])) exact-ML=$(exact_failure(W))")
end
println("Saved $out")
