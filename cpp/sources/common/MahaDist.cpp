#include "MahaDist.h"

void MahaDist(const InputParam &input, const MatrixXd &remainCarrier, const MatrixXd &remainJacobian,
	const VectorXd &theta, VectorXd &MahaDistance)
{
	// compute numerators and denominators
	VectorXd CarTheta = remainCarrier * theta;
	VectorXd tempJacTheta = remainJacobian * theta;
	MatrixXd JacThetaZeta = Eigen::Map<MatrixXd>(tempJacTheta.data(), input.l, remainCarrier.rows());

	// compute norms of denominators
	VectorXd JacTheta(remainCarrier.rows());
	for (auto i = 0; i < remainCarrier.rows(); i++) {
		JacTheta(i) = fabs(JacThetaZeta.col(i).norm());
	}
	VectorXd MahaZeta = (CarTheta.cwiseQuotient(JacTheta)).cwiseAbs();

	// keep the largest distance for each input
	if (input.zeta > 1) {
		MatrixXd zetaCarriers = Eigen::Map<MatrixXd>(MahaZeta.data(), input.zeta, remainCarrier.rows() / input.zeta);
		for (auto i = 0; i < zetaCarriers.cols(); i++) {
			MahaDistance(i) = zetaCarriers.col(i).maxCoeff();
		}
	}
	else {
		MahaDistance = MahaZeta;
	}
	return;
}
