
#include <ctime>
#include <iostream>
#include "pybind11/attr.h"
#include "pybind11/cast.h"
#include "pybind11/pytypes.h"
#include "common.h"
#include "enc.h"
#include "time.h"


namespace SearchAlgorithm {
    std::vector<int> topKIndices(const Eigen::Vector<num_t, Eigen::Dynamic> scores, int k){
        std::vector<int> ret;
        std::vector<std::pair<num_t, int>> scores_idx;
        scores_idx.reserve(scores.size());
        for (int i = 0; i < scores.size(); i++){
            scores_idx.push_back(std::make_pair(scores[i], i));
        }
        // sort with the k-th element as the pivot
        std::nth_element(scores_idx.begin(), scores_idx.begin() + k, scores_idx.end(), [](const std::pair<num_t, int>& a, const std::pair<num_t, int>& b){
            return a.first > b.first;
        });
        // sort the first k elements, the rest are not sorted, make the larger the first
        std::sort(scores_idx.begin(), scores_idx.begin() + k, [](const std::pair<num_t, int>& a, const std::pair<num_t, int>& b){
            return a.first > b.first;
        });
        for (int i = 0; i < k; i++){
            ret.push_back(scores_idx[i].second);
        }
        return ret;
    }

    const num_t _eps = 1e-6;
    inline Eigen::Vector<num_t, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const Eigen::Vector<num_t, FEAT_DIM>& query_matrix){
        if (target.cols() != query_matrix.size()){
            throw std::runtime_error("query size not match");
        }
        Eigen::Matrix<num_t, Eigen::Dynamic, 1> search_scores = target * query_matrix;
        num_t norm_query = query_matrix.norm();
        Eigen::Vector<num_t, Eigen::Dynamic> norm_collection = target.rowwise().norm();
        // std::cout<< "norm_query: " << norm_query << std::endl;
        // std::cout<< "norm_collection: " << norm_collection << std::endl;
        search_scores = search_scores.array() / (norm_query * norm_collection.array() + _eps);
        return search_scores;
    }

    inline Eigen::Vector<num_t, Eigen::Dynamic> l2distance(const MatrixF& target, const Eigen::Vector<num_t, FEAT_DIM>& query_matrix){
        if (target.cols() != query_matrix.size()){
            throw std::runtime_error("query size not match");
        }
        Eigen::Matrix<num_t, Eigen::Dynamic, 1> search_scores = (target.rowwise() - query_matrix.transpose()).rowwise().squaredNorm();
        return search_scores;
    }

    // enum class DistanceMetrics {
    //     COSINE,
    //     L2
    // };
}

// use global buffer to avoid memory allocation
MatrixF g_matrixBuffer(BUFFER_SIZE, FEAT_DIM);

std::vector<num_t> similarityBytesEnc(
    const py::bytes& query_encoded,
    const std::vector<py::bytes>& target_encoded, 
    Eigen::Vector<num_t, Eigen::Dynamic> (*searchFn)(const MatrixF&, const Eigen::Vector<num_t, FEAT_DIM>&)
){
    // Eigen::Vector<num_t, FEAT_DIM> query = Eigen::Map<const Eigen::Vector<num_t, FEAT_DIM>>((num_t*)query_str.data());
    auto query = VectorStringEncode::decode_eigen(query_encoded);

    // First impl: directly map the query string to Eigen::Vector
    // MatrixF target(target_encoded.size(), FEAT_DIM);
    // for (int i = 0; i < target_encoded.size(); i++){
    //     // std::vector<num_t> vec = VectorStringEncode::decode(target_encoded[i]);
    //     auto vec_eigen = VectorStringEncode::decode_eigen(target_encoded[i]);
    //     target.row(i) = vec_eigen;
    // }
    // Eigen::Vector<float, Eigen::Dynamic> scores = searchFn(target, query);

    // Second impl: use global buffer to avoid memory allocation
    // use global buffer to avoid memory allocation, split the target into batches
    auto target_size = target_encoded.size();
    auto n_batch = target_size / BUFFER_SIZE;
    Eigen::Vector<num_t, Eigen::Dynamic> scores(target_size);
    for (unsigned long i = 0; i < n_batch; i++){
        for (unsigned long j = 0; j < BUFFER_SIZE; j++){
            int process_idx = i * BUFFER_SIZE + j;
            auto vec = VectorStringEncode::decode_eigen(target_encoded[process_idx]);
            g_matrixBuffer.row(j) = vec;
        }
        auto scores_batch = searchFn(g_matrixBuffer, query);
        scores.segment(i * BUFFER_SIZE, BUFFER_SIZE) = scores_batch;
    }

    // deal with the remaining
    auto n_remain = target_size % BUFFER_SIZE;
    if (n_remain > 0){
        for (unsigned long j = 0; j < n_remain; j++){
            int process_idx = n_batch * BUFFER_SIZE + j;
            auto vec = VectorStringEncode::decode_eigen(target_encoded[process_idx]);
            g_matrixBuffer.row(j) = vec;
        }
        auto scores_batch = searchFn(g_matrixBuffer, query);
        scores.segment(n_batch * BUFFER_SIZE, n_remain) = scores_batch;
    }

    return std::vector<num_t>(scores.data(), scores.data() + scores.size());
}

std::vector<int> topKIndices(
    const std::vector<num_t>& scores,
    const int k
){
    Eigen::Vector<num_t, Eigen::Dynamic> scores_eigen = Eigen::Map<const Eigen::Vector<num_t, Eigen::Dynamic>>(scores.data(), scores.size());
    return SearchAlgorithm::topKIndices(scores_eigen, k);
}

// namespace py = pybind11;
PYBIND11_MODULE(MODULE_NAME, m) {
    m.doc() = "vector database algorithoms";
    m.attr("FEAT_DIM") = FEAT_DIM;  // for debug
    // m.attr("DISTANCE_TYPE") = py::enum_<SearchAlgorithm::DistanceType>(m, "DistanceType")
    //     .value("COSINE", SearchAlgorithm::DistanceType::COSINE)
    //     .value("L2", SearchAlgorithm::DistanceType::L2)
    //     .export_values();
    // m.def("similarityBytesEnc", &similarityBytesEnc, "distance between a encoded query and a list of targets"); 

    m.def("similarity", [](const py::bytes& query_encoded, const std::vector<py::bytes>& target_encoded){
        return similarityBytesEnc(query_encoded, target_encoded, SearchAlgorithm::cosineSimilarity);
    }, "cosine distance between a encoded query and a list of targets");

    m.def("l2score", [](const py::bytes& query_encoded, const std::vector<py::bytes>& target_encoded){
        return similarityBytesEnc(query_encoded, target_encoded, SearchAlgorithm::l2distance);
    }, "l2 distance between a encoded query and a list of targets");

    m.def("topKIndices", &topKIndices, "top k indices of scores");
    m.def("encode_b64", &VectorStringEncode::encode_b64, "encode vector to string");
    m.def("decode_b64", &VectorStringEncode::decode_b64, "decode string to vector");
    m.def("encode", &VectorStringEncode::encode, "encode vector to bytes");
    m.def("encode_fp64as32", &VectorStringEncode::encode_fp64as32, "encode fp64 vector to bytes");
    m.def("decode", &VectorStringEncode::decode, "decode bytes to vector");
}